import os
import psycopg2
import simplejson as json
from psycopg2.extras import DictCursor

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

        # PostgreSQL连接
        self.conn = psycopg2.connect(
            database="bookstore",
            user="postgres",
            password="0524",
            host="localhost",
            port="5432"
        )

    def get_book_count(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM book")
        count = cur.fetchone()[0]
        cur.close()
        return count
    
    def get_book_info(self, start, size):
        books = []
        cur = self.conn.cursor(cursor_factory=DictCursor)
        
        cur.execute(
            """
            SELECT *
            FROM book
            ORDER BY id
            OFFSET %s
            LIMIT %s
            """,
            (start, size)
        )
        
        rows = cur.fetchall()
        
        for row in rows:
            book = Book()
            book.id = row.get("id")
            book.title = row.get("title")
            book.author = row.get("author")
            book.publisher = row.get("publisher")
            book.original_title = row.get("original_title")
            book.translator = row.get("translator")
            book.pub_year = row.get("pub_year")
            book.pages = row.get("pages")
            book.price = row.get("price")
            book.currency_unit = row.get("currency_unit")
            book.binding = row.get("binding")
            book.isbn = row.get("isbn")
            book.author_intro = row.get("author_intro")
            book.book_intro = row.get("book_intro")
            book.content = row.get("content")
            book.tags = row.get("tags")
            pictures = str(row.get("picture"))

            books.append(book)

        cur.close()
        return books

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()