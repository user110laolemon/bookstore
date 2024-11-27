import json
from datetime import datetime
import psycopg2
from psycopg2 import Error
from be.model import error
from be.model import db_conn
from be.model import store

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_info: dict, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            book_id = book_info.get("id")
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            cur = self.conn.cursor()
            try:
                # 直接插入 store 表，使用 JSONB 类型存储 book_info
                cur.execute(
                    """
                    INSERT INTO store(store_id, book_id, book_info, stock_level)
                    VALUES(%s, %s, %s, %s)
                    """,
                    (store_id, book_id, json.dumps(book_info), stock_level)
                )
                
                self.conn.commit()
                return 200, "ok"
                
            except Exception as e:
                self.conn.rollback()
                return 528, "{}".format(str(e))
            finally:
                cur.close()
                
        except Exception as e:
            return 530, "{}".format(str(e))

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            cur = self.conn.cursor()
            
            # 更新库存
            cur.execute(
                """
                UPDATE store 
                SET stock_level = stock_level + %s
                WHERE store_id = %s AND book_id = %s
                """,
                (add_stock_level, store_id, book_id)
            )

            self.conn.commit()
            cur.close()

        except Error as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            self.conn.rollback()
            return 530, "{}".format(str(e))
        
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            cur = self.conn.cursor()
            
            # 创建商店
            cur.execute(
                """
                INSERT INTO user_store (store_id, user_id)
                VALUES (%s, %s)
                """,
                (store_id, user_id)
            )

            self.conn.commit()
            cur.close()

        except Error as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            self.conn.rollback()
            return 530, "{}".format(str(e))
        
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            cur = self.conn.cursor()
            
            # 检查订单状态
            cur.execute(
                """
                SELECT status 
                FROM new_order 
                WHERE order_id = %s AND store_id = %s
                """,
                (order_id, store_id)
            )
            
            result = cur.fetchone()
            if result is None:
                return error.error_invalid_order_id(order_id)
                
            if result[0] != 'paid':
                return error.error_status_fail(order_id)

            # 更新订单状态为已发货
            cur.execute(
                """
                UPDATE new_order 
                SET status = 'shipped'
                WHERE order_id = %s
                """,
                (order_id,)
            )

            self.conn.commit()
            cur.close()

        except Error as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            self.conn.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"