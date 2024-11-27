import logging
import os
import sys
from flask import Flask
from flask import Blueprint
from flask import request
from be.view import auth
from be.view import seller
from be.view import buyer
from be.view import search
from be.model.store import init_database, init_completed_event
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
    """
    启动自动取消订单服务
    不再使用APScheduler，直接使用OrderAutoCancel的线程机制
    """
    try:
        # OrderAutoCancel的__init__方法会自动启动后台线程
        OrderAutoCancel()
    except Exception as e:
        logging.error(f"启动自动取消订单服务失败: {str(e)}")

def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    
    # 初始化数据库
    try:
        init_database(parent_path)
    except Exception as e:
        logging.error(f"数据库初始化失败: {str(e)}")
        return

    # 配置日志
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # 启动自动取消订单服务
    try:
        start_order_auto_cancel()
    except Exception as e:
        logging.error(f"启动自动取消订单服务失败: {str(e)}")

    # 创建Flask应用
    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)
    app.register_blueprint(search.bp_book)

    init_completed_event.set()
    app.run()
