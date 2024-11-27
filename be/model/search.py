from psycopg2 import Error
from be.model import error
from be.model import db_conn

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            cur = self.conn.cursor()
            
            # 构建WHERE子句
            conditions = ["store.store_id = %s"]
            params = [store_id]
            
            if title:
                conditions.append("book.title ILIKE %s")
                params.append(f"%{title}%")
            if author:
                conditions.append("book.author ILIKE %s")
                params.append(f"%{author}%")
            if publisher:
                conditions.append("book.publisher ILIKE %s")
                params.append(f"%{publisher}%")
            if isbn:
                conditions.append("book.isbn ILIKE %s")
                params.append(f"%{isbn}%")
            if content:
                conditions.append("book.content ILIKE %s")
                params.append(f"%{content}%")
            if tags:
                conditions.append("book.tags ILIKE %s")
                params.append(f"%{tags}%")
            if book_intro:
                conditions.append("book.book_intro ILIKE %s")
                params.append(f"%{book_intro}%")

            # 计算分页
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # 构建完整的SQL查询
            query = """
                SELECT DISTINCT 
                    book.id, book.title, book.author, book.publisher,
                    book.original_title, book.translator, book.pub_year,
                    book.pages, book.price, book.currency_unit,
                    book.binding, book.isbn, book.author_intro,
                    book.book_intro, book.content, book.tags
                FROM store 
                JOIN book ON store.book_id = book.id
                WHERE {}
                LIMIT %s OFFSET %s
            """.format(" AND ".join(conditions))

            cur.execute(query, params)
            
            result = []
            for row in cur.fetchall():
                book = {
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'publisher': row[3],
                    'original_title': row[4],
                    'translator': row[5],
                    'pub_year': row[6],
                    'pages': row[7],
                    'price': row[8],
                    'currency_unit': row[9],
                    'binding': row[10],
                    'isbn': row[11],
                    'author_intro': row[12],
                    'book_intro': row[13],
                    'content': row[14],
                    'tags': row[15]
                }
                result.append(book)

            cur.close()
            return 200, result

        except Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    def search_all(self, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            cur = self.conn.cursor()
            
            # 构建WHERE子句
            conditions = []
            params = []
            
            if title:
                conditions.append("title ILIKE %s")
                params.append(f"%{title}%")
            if author:
                conditions.append("author ILIKE %s")
                params.append(f"%{author}%")
            if publisher:
                conditions.append("publisher ILIKE %s")
                params.append(f"%{publisher}%")
            if isbn:
                conditions.append("isbn ILIKE %s")
                params.append(f"%{isbn}%")
            if content:
                conditions.append("content ILIKE %s")
                params.append(f"%{content}%")
            if tags:
                conditions.append("tags ILIKE %s")
                params.append(f"%{tags}%")
            if book_intro:
                conditions.append("book_intro ILIKE %s")
                params.append(f"%{book_intro}%")

            # 计算分页
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # 构建完整的SQL查询
            where_clause = " AND ".join(conditions)
            query = """
                SELECT 
                    id, title, author, publisher,
                    original_title, translator, pub_year,
                    pages, price, currency_unit,
                    binding, isbn, author_intro,
                    book_intro, content, tags
                FROM book
                {}
                LIMIT %s OFFSET %s
            """.format("WHERE " + where_clause if conditions else "")

            cur.execute(query, params)
            
            result = []
            for row in cur.fetchall():
                book = {
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'publisher': row[3],
                    'original_title': row[4],
                    'translator': row[5],
                    'pub_year': row[6],
                    'pages': row[7],
                    'price': row[8],
                    'currency_unit': row[9],
                    'binding': row[10],
                    'isbn': row[11],
                    'author_intro': row[12],
                    'book_intro': row[13],
                    'content': row[14],
                    'tags': row[15]
                }
                result.append(book)

            cur.close()
            return 200, result

        except Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))