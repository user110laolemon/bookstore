from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, MetaData


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
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []

class BookDB:
    def __init__(self, large: bool = False):
            
        engine = create_engine('postgresql://postgres:0524@localhost:5432/bookstore')

        Session = sessionmaker(bind=engine)
        self.session = Session()

        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        self.Book = Table('book1', metadata, autoload_with=engine)
            

    def get_book_count(self):
        count = self.session.query(self.Book).count()
        return count
        

    def get_book_info(self, start, size) -> [Book]:
        books_in_table = self.session.query(self.Book).all()

        books = []
        for book_in_table in books_in_table:
            book = Book()
            book.id = book_in_table._id
            book.title = book_in_table.title
            book.author = book_in_table.author
            book.publisher = book_in_table.publisher
            book.original_title = book_in_table.original_title
            book.translator = book_in_table.translator
            book.pub_year = book_in_table.pub_year
            book.pages = book_in_table.pages
            book.price = book_in_table.price
            book.currency_unit = book_in_table.currency_unit
            book.binding = book_in_table.binding
            book.isbn = book_in_table.isbn
            book.author_intro = book_in_table.author_intro
            book.book_intro = book_in_table.book_intro
            book.content = book_in_table.contents
            tags = book_in_table.tags

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
                    
            books.append(book)
        
        return books
