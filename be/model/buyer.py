import uuid
import json
from datetime import datetime
from psycopg2 import Error
from be.model import db_conn
from be.model import error

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, books: [dict]) -> (int, str, str):
        order_id = ""
        try:
            if not books:
                return error.error_invalid_order_id("") + (order_id,)

            cur = self.conn.cursor()
            try:
                # 检查用户是否存在
                cur.execute("SELECT user_id FROM \"user\" WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    cur.close()
                    return error.error_non_exist_user_id(user_id) + (order_id,)

                # 检查商店是否存在
                cur.execute("SELECT store_id FROM user_store WHERE store_id = %s", (store_id,))
                if cur.fetchone() is None:
                    cur.close()
                    return error.error_non_exist_store_id(store_id) + (order_id,)

                order_id = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
                total_price = 0

                for book in books:
                    book_id = book.get("id")
                    count = book.get("count")
                    
                    if not book_id or not isinstance(count, int) or count <= 0:
                        self.conn.rollback()
                        cur.close()
                        return error.error_invalid_book_id(book_id) + (order_id,)

                    # 检查图书库存
                    cur.execute(
                        "SELECT stock_level, book_info->>'price' as price FROM store WHERE store_id = %s AND book_id = %s",
                        (store_id, book_id)
                    )
                    row = cur.fetchone()
                    if row is None:
                        self.conn.rollback()
                        cur.close()
                        return error.error_non_exist_book_id(book_id) + (order_id,)

                    stock_level = row[0]
                    price = float(row[1])

                    if stock_level < count:
                        self.conn.rollback()
                        cur.close()
                        return error.error_stock_level_low(book_id) + (order_id,)

                    # 更新库存
                    cur.execute(
                        "UPDATE store SET stock_level = stock_level - %s WHERE store_id = %s AND book_id = %s AND stock_level >= %s",
                        (count, store_id, book_id, count)
                    )
                    if cur.rowcount == 0:
                        self.conn.rollback()
                        cur.close()
                        return error.error_stock_level_low(book_id) + (order_id,)

                    total_price += price * count

                    # 插入订单详情
                    cur.execute(
                        "INSERT INTO new_order_detail(order_id, book_id, count, price) VALUES (%s, %s, %s, %s)",
                        (order_id, book_id, count, price)
                    )

                # 创建订单
                cur.execute(
                    "INSERT INTO new_order(order_id, store_id, user_id, total_price, status) VALUES (%s, %s, %s, %s, %s)",
                    (order_id, store_id, user_id, total_price, 'unpaid')
                )

                self.conn.commit()
                cur.close()
                return 200, "ok", order_id

            except Error as e:
                self.conn.rollback()
                cur.close()
                return error.error_database_operation() + (order_id,)

        except BaseException as e:
            return error.error_database() + (order_id,)

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()
            try:
                cursor.execute(
                    "SELECT order_id, user_id, store_id, total_price, status FROM new_order WHERE order_id = %s",
                    (order_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.close()
                    return error.error_invalid_order_id(order_id)

                order_id = row[0]
                buyer_id = row[1]
                store_id = row[2]
                total_price = float(row[3])
                status = row[4]

                if buyer_id != user_id:
                    cursor.close()
                    return error.error_user_id_match(order_id)

                if status != "unpaid":
                    cursor.close()
                    return error.error_order_status(order_id)

                # 验证用户密码
                cursor.execute(
                    "SELECT password FROM \"user\" WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.close()
                    return error.error_non_exist_user_id(user_id)

                if password != row[0]:
                    cursor.close()
                    return error.error_authorization_fail()

                # 检查余额
                cursor.execute(
                    "SELECT balance FROM user_store WHERE store_id = %s",
                    (store_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.close()
                    return error.error_non_exist_store_id(store_id)

                # 更新订单状态
                cursor.execute(
                    "UPDATE new_order SET status = 'paid' WHERE order_id = %s",
                    (order_id,),
                )

                # 更新商家余额
                cursor.execute(
                    "UPDATE user_store SET balance = balance + %s WHERE store_id = %s",
                    (total_price, store_id),
                )

                self.conn.commit()
                cursor.close()
                return 200, "ok"

            except Error as e:
                self.conn.rollback()
                cursor.close()
                return error.error_database_operation()

        except BaseException as e:
            return error.error_database()

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.cursor()
            try:
                cursor.execute(
                    "SELECT password FROM \"user\" WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.close()
                    return error.error_non_exist_user_id(user_id)

                if row[0] != password:
                    cursor.close()
                    return error.error_authorization_fail()

                cursor.execute(
                    "UPDATE user_store SET balance = balance + %s WHERE user_id = %s",
                    (add_value, user_id),
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        "INSERT INTO user_store(user_id, balance) VALUES (%s, %s)",
                        (user_id, add_value),
                    )

                self.conn.commit()
                cursor.close()
                return 200, "ok"

            except Error as e:
                self.conn.rollback()
                cursor.close()
                return error.error_database_operation()

        except BaseException as e:
            return error.error_database()

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            cur = self.conn.cursor()
            try:
                cur.execute(
                    "SELECT status FROM new_order WHERE order_id = %s AND user_id = %s",
                    (order_id, user_id)
                )
                result = cur.fetchone()
                if result is None:
                    return error.error_invalid_order_id(order_id)

                if result[0] != 'shipped':
                    return error.error_status_fail(order_id)

                cur.execute(
                    "UPDATE new_order SET status = 'received' WHERE order_id = %s",
                    (order_id,)
                )

                self.conn.commit()

            except Error as e:
                self.conn.rollback()
                return error.error_database_operation()
            finally:
                cur.close()

        except BaseException as e:
            return error.error_database()

        return 200, "ok"

    def get_buyer_orders(self, user_id: str, order_id: str = None) -> (int, str, list):
        try:
            cur = self.conn.cursor()
            try:
                # 检查用户是否存在
                cur.execute("SELECT user_id FROM \"user\" WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    cur.close()
                    return error.error_non_exist_user_id(user_id) + ([],)

                if order_id:
                    # 获取特定订单信息
                    cur.execute(
                        """
                        SELECT o.order_id, o.store_id, o.status, o.total_price, o.created_at,
                               array_agg(json_build_object('book_id', d.book_id, 'count', d.count, 'price', d.price)) as books
                        FROM new_order o
                        LEFT JOIN new_order_detail d ON o.order_id = d.order_id
                        WHERE o.user_id = %s AND o.order_id = %s
                        GROUP BY o.order_id, o.store_id, o.status, o.total_price, o.created_at
                        """,
                        (user_id, order_id)
                    )
                else:
                    # 获取所有订单信息
                    cur.execute(
                        """
                        SELECT o.order_id, o.store_id, o.status, o.total_price, o.created_at,
                               array_agg(json_build_object('book_id', d.book_id, 'count', d.count, 'price', d.price)) as books
                        FROM new_order o
                        LEFT JOIN new_order_detail d ON o.order_id = d.order_id
                        WHERE o.user_id = %s
                        GROUP BY o.order_id, o.store_id, o.status, o.total_price, o.created_at
                        """,
                        (user_id,)
                    )

                rows = cur.fetchall()
                orders = []
                for row in rows:
                    order = {
                        'order_id': row[0],
                        'store_id': row[1],
                        'status': row[2],
                        'total_price': float(row[3]),
                        'created_at': row[4].isoformat(),
                        'books': row[5] if row[5][0] is not None else []
                    }
                    orders.append(order)

                cur.close()
                return 200, "ok", orders

            except Error as e:
                cur.close()
                return error.error_database_operation() + ([],)

        except BaseException as e:
            return error.error_database() + ([],)

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            cur = self.conn.cursor()
            try:
                cur.execute(
                    "SELECT status FROM new_order WHERE order_id = %s AND user_id = %s",
                    (order_id, user_id)
                )
                order_info = cur.fetchone()
                if order_info is None:
                    return error.error_non_exist_order_id(order_id)

                if order_info[0] == "paid":
                    # 计算订单总价
                    cur.execute(
                        "SELECT SUM(count * price) FROM new_order_detail WHERE order_id = %s",
                        (order_id,)
                    )
                    order_price = cur.fetchone()[0]

                    # 退还金额
                    cur.execute(
                        "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                        (order_price, user_id)
                    )

                # 更新订单状态
                cur.execute(
                    "UPDATE new_order SET status = 'cancelled' WHERE order_id = %s",
                    (order_id,)
                )

                self.conn.commit()

            except Error as e:
                self.conn.rollback()
                return error.error_database_operation()
            finally:
                cur.close()

        except BaseException as e:
            return error.error_database()

        return 200, "ok"

   
