from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
from be.model import error
from be.model import db_conn
from be.model.db_model import Store as StoreModel, Book as BookModel
from be.model.store import init_completed_event

class Search(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            # 获取商店中的所有书籍ID
            book_ids = self.session.query(StoreModel.book_id).filter(
                StoreModel.store_id == store_id
            ).all()
            book_ids = [bid[0] for bid in book_ids]

            # 构建查询条件
            conditions = [BookModel.id.in_(book_ids)]
            
            if title:
                conditions.append(BookModel.title.ilike(f'%{title}%'))
            if author:
                conditions.append(BookModel.author.ilike(f'%{author}%'))
            if publisher:
                conditions.append(BookModel.publisher.ilike(f'%{publisher}%'))
            if isbn:
                conditions.append(BookModel.isbn.ilike(f'%{isbn}%'))
            if content:
                conditions.append(BookModel.content.ilike(f'%{content}%'))
            if tags:
                conditions.append(BookModel.tags.ilike(f'%{tags}%'))
            if book_intro:
                conditions.append(BookModel.book_intro.ilike(f'%{book_intro}%'))

            # 执行查询
            query = self.session.query(BookModel).filter(and_(*conditions))
            
            # 分页
            offset = (page - 1) * per_page
            books = query.offset(offset).limit(per_page).all()

            # 构建结果
            result = []
            for book in books:
                book_dict = {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'original_title': book.original_title,
                    'translator': book.translator,
                    'pub_year': book.pub_year,
                    'pages': book.pages,
                    'price': book.price,
                    'binding': book.binding,
                    'isbn': book.isbn,
                    'author_intro': book.author_intro,
                    'book_intro': book.book_intro,
                    'content': book.content,
                    'tags': book.tags
                }
                result.append(book_dict)

        except SQLAlchemyError as e:
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))

        return 200, result
    
    def search_all(self, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            # 构建查询条件
            conditions = []
            if title:
                conditions.append(BookModel.title.ilike(f'%{title}%'))
            if author:
                conditions.append(BookModel.author.ilike(f'%{author}%'))
            if publisher:
                conditions.append(BookModel.publisher.ilike(f'%{publisher}%'))
            if isbn:
                conditions.append(BookModel.isbn.ilike(f'%{isbn}%'))
            if content:
                conditions.append(BookModel.content.ilike(f'%{content}%'))
            if tags:
                conditions.append(BookModel.tags.ilike(f'%{tags}%'))
            if book_intro:
                conditions.append(BookModel.book_intro.ilike(f'%{book_intro}%'))

            # 执行查询
            query = self.session.query(BookModel)
            if conditions:
                query = query.filter(or_(*conditions))

            # 分页
            offset = (page - 1) * per_page
            books = query.offset(offset).limit(per_page).all()

            # 构建结果
            result = []
            for book in books:
                book_dict = {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'original_title': book.original_title,
                    'translator': book.translator,
                    'pub_year': book.pub_year,
                    'pages': book.pages,
                    'price': book.price,
                    'binding': book.binding,
                    'isbn': book.isbn,
                    'author_intro': book.author_intro,
                    'book_intro': book.book_intro,
                    'content': book.content,
                    'tags': book.tags
                }
                result.append(book_dict)

        except SQLAlchemyError as e:
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))

        return 200, result