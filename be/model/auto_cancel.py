import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from be.model import error, db_conn
from be.model.db_model import Order as OrderModel
from be.model.store import init_completed_event

class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def cancel_unpaid_orders(self):
        """自动取消超时未支付的订单"""
        try:
            current_time = datetime.now()
            earliest_time = current_time - timedelta(minutes=1)
           
            # 使用原生SQL更新超时未支付的订单
            update_sql = text("""
                UPDATE "order"
                SET status = 'cancelled'
                WHERE status = 'unpaid'
                AND order_time < :earliest_time
                RETURNING id
            """)
       
            result = self.session.execute(
                update_sql,
                {"earliest_time": earliest_time}
            )
       
            affected_rows = result.rowcount
            self.session.commit()
            logging.info(f"Successfully cancelled {affected_rows} unpaid orders")

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"Database error while canceling unpaid orders: {str(e)}")
        except Exception as e:
            logging.error(f"Error canceling unpaid orders: {str(e)}")


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()