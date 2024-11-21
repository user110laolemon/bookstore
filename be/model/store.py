import logging
import threading
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from be.model.db_model import Base

class Store:
    def __init__(self, db_path):
        # PostgreSQL连接URL
        self.engine = create_engine('postgresql://postgres:0524@localhost:5432/bookstore')
        self.init_tables()

    def init_tables(self):
        try:
            # 使用 Base.metadata 创建所有表和索引
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            logging.error("Failed to initialize database: %s", str(e))

    def get_db_conn(self):
        return self.engine


# 全局变量
database_instance: Store = None
init_completed_event = threading.Event()

def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)
    init_completed_event.set()

def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()