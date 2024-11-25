import json
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from be.model import error
from be.model import db_conn
from be.model.store import init_completed_event

class Seller(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            # 检查用户是否存在
            check_user_sql = text("""
                SELECT 1 FROM "user" WHERE user_id = :user_id
            """)
            result = self.session.execute(check_user_sql, {"user_id": user_id})
            if not result.scalar():
                return error.error_non_exist_user_id(user_id)

            # 检查商店是否存在
            check_store_sql = text("""
                SELECT 1 FROM user_store WHERE store_id = :store_id
            """)
            result = self.session.execute(check_store_sql, {"store_id": store_id})
            if not result.scalar():
                return error.error_non_exist_store_id(store_id)

            # 检查图书是否已存在
            check_book_sql = text("""
                SELECT 1 FROM store 
                WHERE store_id = :store_id AND book_id = :book_id
            """)
            result = self.session.execute(check_book_sql, {
                "store_id": store_id,
                "book_id": book_id
            })
            if result.scalar():
                return error.error_exist_book_id(book_id)

            # 验证卖家权限
            check_auth_sql = text("""
                SELECT 1 FROM user_store 
                WHERE user_id = :user_id AND store_id = :store_id
            """)
            result = self.session.execute(check_auth_sql, {
                "user_id": user_id,
                "store_id": store_id
            })
            if not result.scalar():
                return error.error_seller_auth_fail()

            try:
                book_info = json.loads(book_json_str)
            except json.JSONDecodeError:
                return error.error_invalid_parameter()

            # 创建新的商店书籍记录
            add_store_sql = text("""
                INSERT INTO store (store_id, book_id, price, stock_level)
                VALUES (:store_id, :book_id, :price, :stock_level)
            """)
            self.session.execute(add_store_sql, {
                "store_id": store_id,
                "book_id": book_id,
                "price": book_info.get('price'),
                "stock_level": stock_level
            })
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            # 检查用户是否存在
            check_user_sql = text("""
                SELECT 1 FROM "user" WHERE user_id = :user_id
            """)
            result = self.session.execute(check_user_sql, {"user_id": user_id})
            if not result.scalar():
                return error.error_non_exist_user_id(user_id)

            # 检查商店是否存在
            check_store_sql = text("""
                SELECT 1 FROM user_store WHERE store_id = :store_id
            """)
            result = self.session.execute(check_store_sql, {"store_id": store_id})
            if not result.scalar():
                return error.error_non_exist_store_id(store_id)

            # 检查图书是否存在
            check_book_sql = text("""
                SELECT 1 FROM store 
                WHERE store_id = :store_id AND book_id = :book_id
                FOR UPDATE
            """)
            result = self.session.execute(check_book_sql, {
                "store_id": store_id,
                "book_id": book_id
            })
            if not result.scalar():
                return error.error_non_exist_book_id(book_id)

            # 验证卖家权限
            check_auth_sql = text("""
                SELECT 1 FROM user_store 
                WHERE user_id = :user_id AND store_id = :store_id
            """)
            result = self.session.execute(check_auth_sql, {
                "user_id": user_id,
                "store_id": store_id
            })
            if not result.scalar():
                return error.error_seller_auth_fail()

            # 更新库存
            update_stock_sql = text("""
                UPDATE store 
                SET stock_level = stock_level + :add_stock_level
                WHERE store_id = :store_id AND book_id = :book_id
            """)
            self.session.execute(update_stock_sql, {
                "add_stock_level": add_stock_level,
                "store_id": store_id,
                "book_id": book_id
            })
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            # 检查用户是否存在
            check_user_sql = text("""
                SELECT 1 FROM "user" WHERE user_id = :user_id
            """)
            result = self.session.execute(check_user_sql, {"user_id": user_id})
            if not result.scalar():
                return error.error_non_exist_user_id(user_id)

            # 检查商店是否已存在
            check_store_sql = text("""
                SELECT 1 FROM user_store WHERE store_id = :store_id
            """)
            result = self.session.execute(check_store_sql, {"store_id": store_id})
            if result.scalar():
                return error.error_exist_store_id(store_id)

            # 创建新的用户商店关系
            create_store_sql = text("""
                INSERT INTO user_store (user_id, store_id)
                VALUES (:user_id, :store_id)
            """)
            self.session.execute(create_store_sql, {
                "user_id": user_id,
                "store_id": store_id
            })
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        try:
            # 检查商店是否存在
            check_store_sql = text("""
                SELECT 1 FROM user_store WHERE store_id = :store_id
            """)
            result = self.session.execute(check_store_sql, {"store_id": store_id})
            if not result.scalar():
                return error.error_non_exist_store_id(store_id)

            # 查找并更新订单
            update_order_sql = text("""
                UPDATE "order"
                SET status = 'shipped'
                WHERE order_id = :order_id 
                AND store_id = :store_id 
                AND status = 'paid'
                RETURNING 1
            """)
            result = self.session.execute(update_order_sql, {
                "order_id": order_id,
                "store_id": store_id
            })
            
            if not result.scalar():
                # 检查订单是否存在
                check_order_sql = text("""
                    SELECT status FROM "order"
                    WHERE order_id = :order_id AND store_id = :store_id
                """)
                result = self.session.execute(check_order_sql, {
                    "order_id": order_id,
                    "store_id": store_id
                })
                order = result.fetchone()
                if not order:
                    return error.error_invalid_order_id(order_id)
                return error.error_status_fail(order_id)

            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"