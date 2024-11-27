import psycopg2
import threading
import time
from be.model import db_conn

class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        while True:
            try:
                self.cancel_expired_order()
            except Exception as e:
                print(f"Error canceling unpaid orders: {str(e)}")
            time.sleep(5)  # 每5秒检查一次

    def cancel_expired_order(self):
        try:
            cur = self.conn.cursor()
            
            # 使用参数化查询，并确保使用正确的字符串值
            cur.execute(
                """
                UPDATE new_order 
                SET status = %s
                WHERE status = %s 
                AND created_at < NOW() - INTERVAL '30 minutes'
                RETURNING order_id, store_id
                """,
                ('cancelled', 'unpaid')  # 使用参数化查询
            )
            
            expired_orders = cur.fetchall()
            
            for order_id, store_id in expired_orders:
                # 恢复库存
                cur.execute(
                    """
                    SELECT book_id, count 
                    FROM new_order_detail 
                    WHERE order_id = %s
                    """,
                    (order_id,)
                )
                
                order_details = cur.fetchall()
                for book_id, count in order_details:
                    cur.execute(
                        """
                        UPDATE store 
                        SET stock_level = stock_level + %s 
                        WHERE store_id = %s AND book_id = %s
                        """,
                        (count, store_id, book_id)
                    )
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error in cancel_expired_order: {str(e)}")
        finally:
            if cur:
                cur.close()


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()