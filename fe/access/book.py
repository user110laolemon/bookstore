import os
import random
import base64
import simplejson as json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: str
    pictures: [bytes]

    def __init__(self):
        self.pictures = []

class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

        # 连接PostgreSQL
        self.engine = create_engine(
            'postgresql://postgres:0524@localhost:5432/bookstore'
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_book_count(self):
        result = self.session.execute('SELECT COUNT(*) FROM book_info')
        return result.scalar()
    
    def get_book_info(self, start, size):
        books = []
        rows = self.session.execute(
            'SELECT * FROM book_info ORDER BY id OFFSET :start LIMIT :size',
            {'start': start, 'size': size}
        ).fetchall()

        for row in rows:
            book = Book()
            book.id = row.id
            book.title = row.title
            book.author = row.author
            book.publisher = row.publisher
            book.original_title = row.original_title
            book.translator = row.translator
            book.pub_year = row.pub_year
            book.pages = row.pages
            book.price = row.price
            book.binding = row.binding
            book.isbn = row.isbn
            book.author_intro = row.author_intro
            book.book_intro = row.book_intro
            book.content = row.content
            book.tags = row.tags
            book.pictures = []
            if row.picture:
                book.pictures.append(row.picture)

            books.append(book)

        return books