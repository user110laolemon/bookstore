import threading
from datetime import datetime, timedelta
from be.model import error, db_conn
from be.model.store import NewOrder

class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.lock = threading.Lock()  # 添加锁来确保线程安全
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)
        self.cancel_timer.start()

    def cancel_unpaid_orders(self):
        try:
            # 获取当前时间并计算一个分钟之前的时间
            current_time = datetime.now()
            time_interval = current_time - timedelta(minutes=1)

            # 使用锁来确保不会同时有多个线程操作数据库
            with self.lock:
                # 获取所有未支付的订单
                unpaid_order_cursor = self.conn.query(NewOrder).filter_by(status="unpaid").all()

                for order in unpaid_order_cursor:
                    order_time = datetime.fromisoformat(str(order.created_at))
                    # 如果订单超过一分钟前没有支付，进行取消
                    if order_time < time_interval:
                        order.status = "cancelled"

                # 提交更改
                self.conn.commit()

        except Exception as e:
            print(f"Error canceling unpaid orders: {str(e)}")

        # 重新启动定时器，继续每60秒执行
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)
        self.cancel_timer.start()


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()
