import uuid
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from be.model import db_conn, error
from be.model.store import init_completed_event

class Buyer(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            # 检查用户是否存在
            check_user_sql = text("""
                SELECT 1 FROM "user" WHERE user_id = :user_id
            """)
            result = self.session.execute(check_user_sql, {"user_id": user_id})
            if not result.scalar():
                return error.error_non_exist_user_id(user_id) + (order_id,)
            
            # 检查商店是否存在
            check_store_sql = text("""
                SELECT 1 FROM user_store WHERE store_id = :store_id
            """)
            result = self.session.execute(check_store_sql, {"store_id": store_id})
            if not result.scalar():
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            
            # 创建订单
            create_order_sql = text("""
                INSERT INTO "order" (order_id, store_id, user_id, status, order_time)
                VALUES (:order_id, :store_id, :user_id, :status, :order_time)
            """)
            self.session.execute(create_order_sql, {
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "status": "unpaid",
                "order_time": datetime.now()
            })
            
            for book_id, count in id_and_count:
                # 检查并更新库存
                check_stock_sql = text("""
                    SELECT stock_level, price 
                    FROM store 
                    WHERE store_id = :store_id AND book_id = :book_id
                    FOR UPDATE
                """)
                result = self.session.execute(check_stock_sql, {
                    "store_id": store_id,
                    "book_id": book_id
                })
                store = result.fetchone()
                
                if store is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                if store.stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                # 更新库存
                update_stock_sql = text("""
                    UPDATE store 
                    SET stock_level = stock_level - :count
                    WHERE store_id = :store_id AND book_id = :book_id
                """)
                self.session.execute(update_stock_sql, {
                    "count": count,
                    "store_id": store_id,
                    "book_id": book_id
                })
                
                # 创建订单详情
                create_detail_sql = text("""
                    INSERT INTO order_detail (order_id, book_id, count, price)
                    VALUES (:order_id, :book_id, :count, :price)
                """)
                self.session.execute(create_detail_sql, {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": store.price
                })
            
            self.session.commit()
            order_id = uid
        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation() + (order_id,)
        except BaseException as e:
            return error.error_and_message(530, str(e)) + (order_id,)
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # 获取订单信息
            get_order_sql = text("""
                SELECT store_id, status 
                FROM "order" 
                WHERE order_id = :order_id 
                FOR UPDATE
            """)
            result = self.session.execute(get_order_sql, {"order_id": order_id})
            order = result.fetchone()
            
            if not order:
                return error.error_invalid_order_id(order_id)
            
            # 获取卖家信息
            get_seller_sql = text("""
                SELECT user_id 
                FROM user_store 
                WHERE store_id = :store_id
            """)
            result = self.session.execute(get_seller_sql, {"store_id": order.store_id})
            seller_store = result.fetchone()
            
            if not seller_store:
                return error.error_non_exist_store_id(order.store_id)
            
            # 验证买家
            check_buyer_sql = text("""
                SELECT balance 
                FROM "user" 
                WHERE user_id = :user_id AND password = :password 
                FOR UPDATE
            """)
            result = self.session.execute(check_buyer_sql, {
                "user_id": user_id,
                "password": password
            })
            buyer = result.fetchone()
            
            if not buyer:
                return error.error_authorization_fail()
            
            # 计算总价
            get_total_sql = text("""
                SELECT SUM(price * count) as total 
                FROM order_detail 
                WHERE order_id = :order_id
            """)
            result = self.session.execute(get_total_sql, {"order_id": order_id})
            total_price = result.scalar()
            
            if buyer.balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            
            # 更新买家和卖家余额
            update_buyer_sql = text("""
                UPDATE "user" 
                SET balance = balance - :amount 
                WHERE user_id = :user_id
            """)
            update_seller_sql = text("""
                UPDATE "user" 
                SET balance = balance + :amount 
                WHERE user_id = :user_id
            """)
            
            self.session.execute(update_buyer_sql, {
                "amount": total_price,
                "user_id": user_id
            })
            self.session.execute(update_seller_sql, {
                "amount": total_price,
                "user_id": seller_store.user_id
            })
            
            # 更新订单状态
            update_order_sql = text("""
                UPDATE "order" 
                SET status = 'paid' 
                WHERE order_id = :order_id
            """)
            self.session.execute(update_order_sql, {"order_id": order_id})
            
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def add_funds(self, user_id: str, password: str, add_value: float) -> (int, str):
        try:
            # 验证买家密码
            check_buyer_sql = text("""
                SELECT balance 
                FROM "user" 
                WHERE user_id = :user_id AND password = :password 
                FOR UPDATE
            """)
            result = self.session.execute(check_buyer_sql, {
                "user_id": user_id,
                "password": password
            })
            buyer = result.fetchone()
            
            if not buyer:
                return error.error_authorization_fail()
            
            # 更新余额
            update_balance_sql = text("""
                UPDATE "user" 
                SET balance = balance + :add_value 
                WHERE user_id = :user_id
                RETURNING user_id
            """)
            
            result = self.session.execute(update_balance_sql, {
                "add_value": add_value,
                "user_id": user_id
            })
            
            if not result.scalar():
                return error.error_database_operation()
            
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

   
