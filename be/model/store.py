import logging
import threading
import psycopg2
from psycopg2 import Error

init_completed_event = threading.Event()

class Store:
    def __init__(self):
        self.init_tables()
        init_completed_event.set()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            cur = conn.cursor()

            # 创建用户表和索引
            cur.execute("""
                CREATE TABLE IF NOT EXISTS "user" (
                    user_id VARCHAR PRIMARY KEY,
                    password VARCHAR NOT NULL,
                    balance NUMERIC(10,2) NOT NULL,
                    token TEXT,
                    terminal TEXT
                )
            """)

            # 创建用户商店表和索引
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_store (
                    user_id VARCHAR NOT NULL,
                    store_id VARCHAR NOT NULL,
                    PRIMARY KEY (user_id, store_id)
                )
            """)

            # 创建商店表和索引
            cur.execute("""
                CREATE TABLE IF NOT EXISTS store (
                    store_id VARCHAR NOT NULL,
                    book_id VARCHAR NOT NULL,
                    book_info JSONB NOT NULL,
                    stock_level INTEGER NOT NULL,
                    PRIMARY KEY (store_id, book_id)
                )
            """)

            # 创建订单表和索引
            cur.execute("""
                CREATE TABLE IF NOT EXISTS new_order (
                    order_id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255),
                    store_id VARCHAR(255),
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建订单详情表和索引
            cur.execute("""
                CREATE TABLE IF NOT EXISTS new_order_detail (
                    order_id VARCHAR NOT NULL,
                    book_id VARCHAR NOT NULL,
                    count INTEGER NOT NULL,
                    price NUMERIC(10,2) NOT NULL,
                    PRIMARY KEY (order_id, book_id)
                )
            """)

            conn.commit()
            cur.close()
            conn.close()

        except Error as e:
            logging.error(e)

    def get_db_conn(self):
        conn = psycopg2.connect(
            database="bookstore",
            user="postgres",
            password="0524",
            host="localhost",
            port="5432"
        )
        return conn

database_instance = None

def init_database(db_path):
    global database_instance
    database_instance = Store()

def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()