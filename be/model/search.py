from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from be.model import error
from be.model import db_conn
from be.model.store import init_completed_event

class Search(db_conn.DBConn):
    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            # 检查商店是否存在
            check_store_sql = text("""
                SELECT 1 FROM user_store WHERE store_id = :store_id
            """)
            result = self.session.execute(check_store_sql, {"store_id": store_id})
            if not result.scalar():
                return error.error_non_exist_store_id(store_id)
            
            # 构建查询条件
            conditions = ["b.id IN (SELECT book_id FROM store WHERE store_id = :store_id)"]
            params = {"store_id": store_id}
            
            if title:
                conditions.append("b.title ILIKE :title")
                params["title"] = f"%{title}%"
            if author:
                conditions.append("b.author ILIKE :author")
                params["author"] = f"%{author}%"
            if publisher:
                conditions.append("b.publisher ILIKE :publisher")
                params["publisher"] = f"%{publisher}%"
            if isbn:
                conditions.append("b.isbn ILIKE :isbn")
                params["isbn"] = f"%{isbn}%"
            if content:
                conditions.append("b.content ILIKE :content")
                params["content"] = f"%{content}%"
            if tags:
                conditions.append("b.tags ILIKE :tags")
                params["tags"] = f"%{tags}%"
            if book_intro:
                conditions.append("b.book_intro ILIKE :book_intro")
                params["book_intro"] = f"%{book_intro}%"
            
            where_clause = " AND ".join(conditions)
            params["offset"] = (page - 1) * per_page
            params["limit"] = per_page

            search_sql = text(f"""
                SELECT b.* FROM book_info b
                WHERE {where_clause}
                OFFSET :offset LIMIT :limit
            """)
            
            result = self.session.execute(search_sql, params)
            books = result.fetchall()

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
            params = {
                "offset": (page - 1) * per_page,
                "limit": per_page
            }
            
            if title:
                conditions.append("title ILIKE :title")
                params["title"] = f"%{title}%"
            if author:
                conditions.append("author ILIKE :author")
                params["author"] = f"%{author}%"
            if publisher:
                conditions.append("publisher ILIKE :publisher")
                params["publisher"] = f"%{publisher}%"
            if isbn:
                conditions.append("isbn ILIKE :isbn")
                params["isbn"] = f"%{isbn}%"
            if content:
                conditions.append("content ILIKE :content")
                params["content"] = f"%{content}%"
            if tags:
                conditions.append("tags ILIKE :tags")
                params["tags"] = f"%{tags}%"
            if book_intro:
                conditions.append("book_intro ILIKE :book_intro")
                params["book_intro"] = f"%{book_intro}%"

            where_clause = " OR ".join(conditions) if conditions else "1=1"
            
            search_sql = text(f"""
                SELECT * FROM book_info
                WHERE {where_clause}
                OFFSET :offset LIMIT :limit
            """)
            
            result = self.session.execute(search_sql, params)
            books = result.fetchall()

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