from fe.bench.workload import Workload
from fe.bench.workload import NewOrder
from fe.bench.workload import Payment
from fe.bench.workload import ShipOrder
from fe.bench.workload import ReceiveOrder
import time
import threading

# 性能测试会话类，用于模拟用户购买和支付的行为
class Session(threading.Thread):
    def __init__(self, wl: Workload):
        threading.Thread.__init__(self)
        self.workload = wl
        self.new_order_request = []
        self.payment_request = []
        self.shipment_request = []                 
        self.receive_request = []
        
        self.payment_i = 0
        self.new_order_i = 0
        self.shipment_i = 0                    
        self.receive_i = 0
        
        self.payment_ok = 0
        self.new_order_ok = 0
        self.shipment_ok = 0              
        self.receive_ok = 0
        
        self.time_new_order = 0
        self.time_payment = 0
        self.time_shipment = 0                    
        self.time_receive = 0
        
        self.thread = None
        self.gen_procedure()

    def gen_procedure(self):
        """
        生成订单请求，根据工作负载配置生成指定数量的订单请求
        """
        for i in range(0, self.workload.procedure_per_session):
            new_order = self.workload.get_new_order()
            self.new_order_request.append(new_order)

    def run(self):
        self.run_gut()

    def run_gut(self):
        # 遍历所有订单请求
        for new_order in self.new_order_request:
            # 记录订单请求开始时间
            before = time.time()
            # 执行订单请求
            ok, order_id = new_order.run()
            # 记录订单请求结束时间
            after = time.time()
            # 计算订单请求时间
            self.time_new_order = self.time_new_order + after - before
            # 订单请求次数
            self.new_order_i = self.new_order_i + 1
            # 订单请求成功
            if ok:
                self.new_order_ok = self.new_order_ok + 1
                payment = Payment(new_order.buyer, order_id)
                self.payment_request.append(payment)
                
            if True:
                self.workload.update_stat(
                    self.new_order_i,
                    self.payment_i,
                    self.shipment_i,                         
                    self.receive_i,
                    self.new_order_ok,
                    self.payment_ok,
                    self.shipment_ok,                         
                    self.receive_ok,
                    self.time_new_order,
                    self.time_payment,
                    self.time_shipment,                       
                    self.time_receive
                )
                for payment in self.payment_request:
                    before = time.time()
                    ok = payment.run()
                    after = time.time()
                    self.time_payment = self.time_payment + after - before
                    self.payment_i = self.payment_i + 1
                    if ok:
                        self.payment_ok = self.payment_ok + 1
                        shipment = ShipOrder(new_order.store_id, order_id)     
                        self.shipment_request.append(shipment)
                        
                for shipment in self.shipment_request:               
                    before = time.time()
                    ok = shipment.run()
                    after = time.time()
                    self.time_shipment = self.time_shipment + after - before
                    self.shipment_i = self.shipment_i + 1
                    if ok:
                        self.shipment_ok = self.shipment_ok + 1
                        receive = ReceiveOrder(new_order.buyer, order_id)
                        self.receive_request.append(receive)

                for receive in self.receive_request:                   
                    before = time.time()
                    ok = receive.run()
                    after = time.time()
                    self.time_receive = self.time_receive + after - before
                    self.receive_i = self.receive_i + 1
                    if ok:
                        self.receive_ok = self.receive_ok + 1
                        
                self.payment_request = []
                self.shipment_request = []                      
                self.receive_request = []
