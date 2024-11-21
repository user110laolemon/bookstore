from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from be.model import store
from be.model.db_model import (
    User as UserModel,
    Store as StoreModel,
    UserStore as UserStoreModel,
    Order as OrderModel
)

class DBConn:
    """数据库连接类，处理与PostgreSQL的连接和基本查询操作"""
    def __init__(self):
        self.engine = store.get_db_conn()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def __del__(self):
        """析构函数，确保session被正确关闭"""
        if hasattr(self, 'session'):
            self.session.close()

    def user_id_exist(self, user_id: str) -> bool:
        """
        检查用户是否存在
        :param user_id: 用户ID
        :return: 如果用户存在返回True，否则返回False
        """
        try:
            user = self.session.query(UserModel).filter(
                UserModel.user_id == user_id
            ).first()
            return user is not None
        except SQLAlchemyError:
            return False

    def book_id_exist(self, store_id: str, book_id: str) -> bool:
        """
        检查特定商店中的图书是否存在
        :param store_id: 商店ID
        :param book_id: 图书ID
        :return: 如果图书存在返回True，否则返回False
        """
        try:
            book = self.session.query(StoreModel).filter(
                StoreModel.store_id == store_id,
                StoreModel.book_id == book_id
            ).first()
            return book is not None
        except SQLAlchemyError:
            return False

    def store_id_exist(self, store_id: str) -> bool:
        """
        检查商店是否存在
        :param store_id: 商店ID
        :return: 如果商店存在返回True，否则返回False
        """
        try:
            store = self.session.query(UserStoreModel).filter(
                UserStoreModel.store_id == store_id
            ).first()
            return store is not None
        except SQLAlchemyError:
            return False

    def order_id_exist(self, user_id: str, order_id: str) -> bool:
        """
        检查用户的订单是否存在
        :param user_id: 用户ID
        :param order_id: 订单ID
        :return: 如果订单存在返回True，否则返回False
        """
        try:
            order = self.session.query(OrderModel).filter(
                OrderModel.user_id == user_id,
                OrderModel.order_id == order_id
            ).first()
            return order is not None
        except SQLAlchemyError:
            return False

    def user_store_exist(self, user_id: str, store_id: str) -> bool:
        """
        检查用户是否拥有该商店
        :param user_id: 用户ID
        :param store_id: 商店ID
        :return: 如果关系存在返回True，否则返回False
        """
        try:
            relation = self.session.query(UserStoreModel).filter(
                UserStoreModel.user_id == user_id,
                UserStoreModel.store_id == store_id
            ).first()
            return relation is not None
        except SQLAlchemyError:
            return False

    def close_session(self):
        """显式关闭session"""
        if hasattr(self, 'session'):
            self.session.close()