import threading
from datetime import datetime, timedelta
from be.model import error, db_conn
from be.model.db_model import Order as OrderModel

class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def cancel_unpaid_orders(self):
        try:
            current_time = datetime.now()
            earliest_time = current_time - timedelta(minutes=1)

            # 查找并更新超时未支付的订单
            unpaid_orders = self.session.query(OrderModel).filter(
                OrderModel.status == "unpaid",
                OrderModel.order_time < earliest_time.isoformat()
            )

            for order in unpaid_orders:
                order.status = "cancelled"
            
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error canceling unpaid orders: {str(e)}")
            # 删除 finally 块，因为 DBConn 的析构函数会处理 session 的关闭


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()