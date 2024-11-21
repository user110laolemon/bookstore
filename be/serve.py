import logging
import os
import sys
from flask import Flask
from flask import Blueprint
from flask import request
from be.view import auth
from be.view import seller
from be.view import buyer

# 导入搜索书籍
from be.view import search
# 导入自动取消订单
from apscheduler.schedulers.background import BackgroundScheduler     
from be.model.auto_cancel import OrderAutoCancel

from be.model.store import init_database, init_completed_event

from apscheduler.schedulers.background import BackgroundScheduler     
from be.model.auto_cancel import OrderAutoCancel                   

bp_shutdown = Blueprint("shutdown", __name__)

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."

def start_order_auto_cancel():
    scheduler = BackgroundScheduler()
    scheduler.add_job(OrderAutoCancel().cancel_unpaid_orders, 'interval', seconds = 5)  
    scheduler.start()

def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    init_database(parent_path)

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # 自动取消订单开启
    start_order_auto_cancel()

    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)

    # 搜索书籍
    app.register_blueprint(search.bp_book)

    init_completed_event.set()
    app.run()
