from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    user_id = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    token = Column(String)
    terminal = Column(String)

    __table_args__ = (
        Index('idx_user_id', 'user_id', unique=True),
    )

class UserStore(Base):
    __tablename__ = 'user_store'
    
    user_id = Column(String, ForeignKey('user.user_id'), primary_key=True)
    store_id = Column(String, primary_key=True)

    __table_args__ = (
        Index('idx_user_store', 'user_id', 'store_id'),
    )

class Store(Base):
    __tablename__ = 'store'
    
    store_id = Column(String, primary_key=True)
    book_id = Column(String, ForeignKey('book_info.id'), primary_key=True)
    price = Column(Float, nullable=False)
    stock_level = Column(Integer, nullable=False)

    __table_args__ = (
        Index('idx_store', 'store_id', 'book_id'),
    )

class Order(Base):
    __tablename__ = 'new_order'
    
    order_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('user.user_id'))
    store_id = Column(String)
    status = Column(String, nullable=False)  # 订单状态
    total_price = Column(Float)
    order_time = Column(String)

    __table_args__ = (
        Index('idx_order_id', 'order_id', unique=True),
    )

class OrderDetail(Base):
    __tablename__ = 'new_order_detail'
    
    order_id = Column(String, ForeignKey('new_order.order_id'), primary_key=True)
    book_id = Column(String, ForeignKey('book_info.id'), primary_key=True)
    count = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    __table_args__ = (
        Index('idx_order_detail', 'order_id', 'book_id'),
    )

class Book(Base):
    __tablename__ = 'book_info'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    original_title = Column(String)
    translator = Column(String)
    pub_year = Column(String)
    pages = Column(Integer)
    price = Column(Float)
    binding = Column(String)
    isbn = Column(String)
    author_intro = Column(String)
    book_intro = Column(String)
    content = Column(String)
    tags = Column(String)
    picture = Column(String)