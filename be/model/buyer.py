import uuid
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from be.model import db_conn, error
from be.model.db_model import (
    User as UserModel,
    Store as StoreModel,
    Order as OrderModel,
    OrderDetail as OrderDetailModel,
    UserStore as UserStoreModel
)
from be.model.store import init_completed_event

class Buyer(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            
            # 检查商店是否存在
            store_exist = self.session.query(UserStoreModel).filter(
                UserStoreModel.store_id == store_id
            ).first()
            if not store_exist:
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            # 获取卖家信息
            seller = self.session.query(UserStoreModel).filter(
                UserStoreModel.store_id == store_id
            ).first()
            
            # 创建订单
            new_order = OrderModel(
                order_id=uid,
                store_id=store_id,
                user_id=user_id,
                status="unpaid",
                order_time=datetime.now()
            )

            for book_id, count in id_and_count:
                store = self.session.query(StoreModel).filter(
                    and_(
                        StoreModel.store_id == store_id,
                        StoreModel.book_id == book_id
                    )
                ).with_for_update().first()

                if store is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                if store.stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 更新库存
                store.stock_level -= count

                # 创建订单详情
                order_detail = OrderDetailModel(
                    order_id=uid,
                    book_id=book_id,
                    count=count,
                    price=store.price
                )
                self.session.add(order_detail)

            self.session.add(new_order)
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
            order = self.session.query(OrderModel).filter(
                OrderModel.order_id == order_id
            ).with_for_update().first()

            if not order:
                return error.error_invalid_order_id(order_id)

            # 获取卖家信息
            seller_store = self.session.query(UserStoreModel).filter(
                UserStoreModel.store_id == order.store_id
            ).first()
            if not seller_store:
                return error.error_non_exist_store_id(order.store_id)

            # 验证用户
            buyer = self.session.query(UserModel).filter(
                and_(
                    UserModel.user_id == user_id,
                    UserModel.password == password
                )
            ).with_for_update().first()

            if not buyer:
                return error.error_authorization_fail()

            # 计算总价
            order_details = self.session.query(OrderDetailModel).filter(
                OrderDetailModel.order_id == order_id
            ).all()

            total_price = sum(detail.price * detail.count for detail in order_details)

            if buyer.balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 更新买家余额
            buyer.balance -= total_price
            
            # 更新卖家余额
            seller = self.session.query(UserModel).filter(
                UserModel.user_id == seller_store.user_id
            ).with_for_update().first()
            seller.balance += total_price
            
            order.status = "paid"
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))

        return 200, "ok"

    def add_funds(self, user_id: str, password: str, add_value: float) -> (int, str):
        try:
            user = self.session.query(UserModel).filter(
                and_(
                    UserModel.user_id == user_id,
                    UserModel.password == password
                )
            ).with_for_update().first()

            if not user:
                return error.error_authorization_fail()

            user.balance += add_value
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))

        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            order = self.session.query(OrderModel).filter(
                and_(
                    OrderModel.order_id == order_id,
                    OrderModel.user_id == user_id
                )
            ).with_for_update().first()

            if not order or order.status != "shipped":
                return error.error_status_fail(order_id)

            order.status = "received"
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))

        return 200, "ok"

    def get_buyer_orders(self, user_id: str) -> (int, str, list):
        try:
            orders = self.session.query(OrderModel).filter(
                OrderModel.user_id == user_id
            ).all()

            buyer_orders = [{
                'store_id': order.store_id,
                'order_id': order.order_id,
                'status': order.status
            } for order in orders]

        except SQLAlchemyError as e:
            return error.error_database_operation() + ([],)
        except BaseException as e:
            return error.error_and_message(530, str(e)) + ([],)

        return 200, "ok", buyer_orders

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            order = self.session.query(OrderModel).filter(
                and_(
                    OrderModel.order_id == order_id,
                    OrderModel.user_id == user_id
                )
            ).with_for_update().first()

            if not order:
                return error.error_non_exist_order_id(order_id)

            if order.status == "paid":
                # 计算退款金额
                order_details = self.session.query(OrderDetailModel).filter(
                    OrderDetailModel.order_id == order_id
                ).all()

                refund_amount = sum(detail.price * detail.count for detail in order_details)

                # 更新用户余额
                user = self.session.query(UserModel).filter(
                    UserModel.user_id == user_id
                ).with_for_update().first()
                
                user.balance += refund_amount

                # 更新卖家余额
                seller_store = self.session.query(UserStoreModel).filter(
                    UserStoreModel.store_id == order.store_id
                ).first()
                
                seller = self.session.query(UserModel).filter(
                    UserModel.user_id == seller_store.user_id
                ).with_for_update().first()
                
                seller.balance -= refund_amount

                # 恢复库存
                order_details = self.session.query(OrderDetailModel).filter(
                    OrderDetailModel.order_id == order_id
                ).all()
                
                for detail in order_details:
                    store = self.session.query(StoreModel).filter(
                        and_(
                            StoreModel.store_id == order.store_id,
                            StoreModel.book_id == detail.book_id
                        )
                    ).with_for_update().first()
                    
                    if store:
                        store.stock_level += detail.count

            order.status = "cancelled"
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))

        return 200, "ok"