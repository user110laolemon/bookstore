import logging
import threading
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'bookstore',
    'user': 'postgres',
    'password': '0524'
}

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置数据库连接参数"""
    cursor = dbapi_connection.cursor()
    cursor.execute("SET timezone TO 'UTC'")
    cursor.close()

class Store:
    def __init__(self, db_path=None):
        """初始化数据库连接"""
        try:
            # 构建数据库 URL
            db_url = 'postgresql://postgres:0524@localhost:5432/bookstore'
            
            # 配置数据库引擎
            self.engine = create_engine(
                db_url,
                echo=False,  # 设置为 True 可以查看 SQL 语句
                pool_size=10,  # 连接池大小
                max_overflow=20,  # 超出 pool_size 后最多可以创建的连接数
                pool_timeout=30,  # 连接池获取连接的超时时间
                pool_recycle=1800,  # 连接重置时间（秒）
                pool_pre_ping=True,  # 连接前检查
                poolclass=QueuePool,  # 使用队列池
                isolation_level='READ COMMITTED'  # 设置隔离级别
            )
            
            self.init_tables()
            logging.info("Database connection initialized successfully")
            
        except Exception as e:
            logging.error("Failed to initialize database connection: %s", str(e))
            raise

    def init_tables(self):
        """初始化数据库表"""
        try:
            with self.engine.connect() as conn:
                # 用户表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS "user" (
                        user_id VARCHAR(100) PRIMARY KEY,
                        password VARCHAR(100) NOT NULL,
                        balance FLOAT NOT NULL DEFAULT 0.0,
                        token VARCHAR(200),
                        terminal VARCHAR(200)
                    );
                    CREATE INDEX IF NOT EXISTS idx_user_id ON "user" (user_id);
                """)

                # 用户商店表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_store (
                        user_id VARCHAR(100) REFERENCES "user" (user_id) ON DELETE CASCADE,
                        store_id VARCHAR(100),
                        PRIMARY KEY (user_id, store_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_user_store ON user_store (user_id, store_id);
                """)

                # 商店表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS store (
                        store_id VARCHAR(100),
                        book_id VARCHAR(100),
                        price FLOAT NOT NULL,
                        stock_level INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (store_id, book_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_store ON store (store_id, book_id);
                """)

                # 订单表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS "order" (
                        order_id VARCHAR(100) PRIMARY KEY,
                        user_id VARCHAR(100) REFERENCES "user" (user_id) ON DELETE CASCADE,
                        store_id VARCHAR(100),
                        status VARCHAR(20) NOT NULL,
                        total_price FLOAT DEFAULT 0.0,
                        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_order_id ON "order" (order_id);
                    CREATE INDEX IF NOT EXISTS idx_user_order ON "order" (user_id, order_id);
                """)

                # 订单详情表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS order_detail (
                        order_id VARCHAR(100) REFERENCES "order" (order_id) ON DELETE CASCADE,
                        book_id VARCHAR(100),
                        count INTEGER NOT NULL,
                        price FLOAT NOT NULL,
                        PRIMARY KEY (order_id, book_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_order_detail ON order_detail (order_id, book_id);
                """)

                # 图书信息表
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS book_info (
                        id VARCHAR(100) PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        author VARCHAR(200),
                        publisher VARCHAR(200),
                        original_title VARCHAR(200),
                        translator VARCHAR(200),
                        pub_year VARCHAR(20),
                        pages INTEGER,
                        price FLOAT,
                        binding VARCHAR(100),
                        isbn VARCHAR(50) UNIQUE,
                        author_intro TEXT,
                        book_intro TEXT,
                        content TEXT,
                        tags TEXT,
                        picture TEXT
                    );
                    CREATE INDEX IF NOT EXISTS idx_book_isbn ON book_info (isbn);
                    CREATE INDEX IF NOT EXISTS idx_book_title ON book_info (title);
                """)

                conn.commit()
                logging.info("Database tables initialized successfully")
                
        except SQLAlchemyError as e:
            logging.error("Failed to initialize database tables: %s", str(e))
            raise

    def get_db_conn(self):
        """获取数据库连接"""
        return self.engine

    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logging.info("Database connection closed")


# 全局变量和事件
database_instance: Store = None
init_completed_event = threading.Event()

def init_database(db_path=None):
    """初始化数据库实例"""
    global database_instance
    try:
        database_instance = Store(db_path)
        init_completed_event.set()
        logging.info("Database instance initialized successfully")
    except Exception as e:
        logging.error("Failed to initialize database instance: %s", str(e))
        raise

def get_db_conn():
    """获取数据库连接实例"""
    global database_instance
    if database_instance is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return database_instance.get_db_conn()

def close_database():
    """关闭数据库连接"""
    global database_instance
    if database_instance:
        try:
            database_instance.close()
            database_instance = None
            init_completed_event.clear()
            logging.info("Database connection closed successfully")
        except Exception as e:
            logging.error("Error closing database connection: %s", str(e))