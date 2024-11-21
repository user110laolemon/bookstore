import json
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from be.model import error
from be.model import db_conn
from be.model.db_model import (
    Store as StoreModel,
    UserStore as UserStoreModel,
    Order as OrderModel,
    Book as BookModel
)
from be.model.store import init_completed_event

class Seller(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # 验证卖家权限
            if not self.user_store_exist(user_id, store_id):
                return error.error_seller_auth_fail()

            try:
                book_info = json.loads(book_json_str)
            except json.JSONDecodeError:
                return error.error_invalid_parameter()

            # 创建新的商店书籍记录
            new_store = StoreModel(
                store_id=store_id,
                book_id=book_id,
                price=book_info.get('price'),
                stock_level=stock_level
            )
            self.session.add(new_store)
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # 验证卖家权限
            if not self.user_store_exist(user_id, store_id):
                return error.error_seller_auth_fail()

            # 更新库存
            store = self.session.query(StoreModel).filter(
                and_(
                    StoreModel.store_id == store_id,
                    StoreModel.book_id == book_id
                )
            ).with_for_update().first()
            
            store.stock_level += add_stock_level
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 创建新的用户商店关系
            new_user_store = UserStoreModel(
                user_id=user_id,
                store_id=store_id
            )
            self.session.add(new_user_store)
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            # 查找订单
            order = self.session.query(OrderModel).filter(
                and_(
                    OrderModel.order_id == order_id,
                    OrderModel.store_id == store_id
                )
            ).with_for_update().first()

            if not order:
                return error.error_invalid_order_id(order_id)
            if order.status != "paid":
                return error.error_status_fail(order_id)

            # 更新订单状态
            order.status = "shipped"
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"