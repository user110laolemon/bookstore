from be.model import store

class DBConn:
    """
    数据库连接类，处理与PostgreSQL的连接和基本查询操作
    """
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        """
        检查用户是否存在
        :param user_id: 用户ID
        :return: 如果用户存在返回True，否则返回False
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT 1 FROM \"user\" WHERE user_id = %s",
                (user_id,)
            )
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close()

    def book_id_exist(self, store_id, book_id):
        """
        检查特定商店中的图书是否存在
        :param store_id: 商店ID
        :param book_id: 图书ID
        :return: 如果图书存在返回True，否则返回False
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT 1 FROM store WHERE store_id = %s AND book_id = %s",
                (store_id, book_id)
            )
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close()

    def store_id_exist(self, store_id):
        """
        检查商店是否存在
        :param store_id: 商店ID
        :return: 如果商店存在返回True，否则返回False
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT 1 FROM user_store WHERE store_id = %s",
                (store_id,)
            )
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close()
    
    def order_id_exist(self, user_id, order_id):
        """
        检查用户的订单是否存在
        :param user_id: 用户ID
        :param order_id: 订单ID
        :return: 如果订单存在返回True，否则返回False
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT 1 FROM new_order WHERE user_id = %s AND order_id = %s",
                (user_id, order_id)
            )
            result = cur.fetchone()
            return result is not None
        finally:
            cur.close()

    def __del__(self):
        """
        析构函数，确保数据库连接被正确关闭
        """
        if hasattr(self, 'conn'):
            self.conn.close()