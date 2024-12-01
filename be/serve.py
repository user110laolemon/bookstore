import logging
import os
from flask import Flask
from flask import Blueprint
from flask import request
from be.view import auth, search
from be.view import seller
from be.view import buyer
from be.model.store import init_database
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
    scheduler.add_job(OrderAutoCancel().cancel_unpaid_orders, 'interval', minutes=1)
    scheduler.start()

def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    init_database()

    logging.basicConfig(filename=log_file, level=logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    start_order_auto_cancel()
    
    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)
    app.register_blueprint(search.bp_search)
    app.run()
