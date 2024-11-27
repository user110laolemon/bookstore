# -*- coding: utf-8 -*-
import sqlite3
import psycopg2
import sys
import os

def migrate_books():
    try:
        # 确保SQLite数据库文件存在
        db_path = os.path.join('.', 'fe', 'data', 'book.db')
        if not os.path.exists(db_path):
            print(f"SQLite数据库文件不存在: {db_path}")
            return False

        # 连接SQLite
        sqlite_conn = sqlite3.connect(db_path)
        sqlite_cursor = sqlite_conn.cursor()

        # 连接PostgreSQL
        pg_conn = psycopg2.connect(
            database="bookstore",
            user="postgres",
            password="0524",
            host="localhost",
            port="5432"
        )
        pg_cursor = pg_conn.cursor()

        # 删除已存在的表
        pg_cursor.execute("DROP TABLE IF EXISTS book")

        # 创建book表
        pg_cursor.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                publisher TEXT,
                original_title TEXT,
                translator TEXT,
                pub_year TEXT,
                pages INTEGER,
                price INTEGER,
                currency_unit TEXT,
                binding TEXT,
                isbn TEXT,
                author_intro TEXT,
                book_intro TEXT,
                content TEXT,
                tags TEXT,
                picture BYTEA
            )
        """)

        # 查询SQLite数据
        sqlite_cursor.execute("SELECT * FROM book")
        book_records = sqlite_cursor.fetchall()
        
        print(f"开始迁移 {len(book_records)} 条记录...")

        # 批量插入数据
        for i, record in enumerate(book_records):
            try:
                pg_cursor.execute("""
                    INSERT INTO book (
                        id, title, author, publisher, original_title, translator, 
                        pub_year, pages, price, currency_unit, binding, isbn, 
                        author_intro, book_intro, content, tags, picture
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, record)
                
                if (i + 1) % 100 == 0:
                    print(f"已处理 {i + 1} 条记录...")
                    pg_conn.commit()  # 定期提交

            except Exception as e:
                print(f"插入记录 {record[0]} 时出错: {str(e)}")
                continue

        # 最终提交
        pg_conn.commit()
        print("数据迁移完成")

        # 验证数据
        pg_cursor.execute("SELECT COUNT(*) FROM book")
        pg_count = pg_cursor.fetchone()[0]
        print(f"PostgreSQL中的记录数: {pg_count}")

        return True

    except Exception as e:
        print(f"迁移过程出错: {str(e)}")
        return False

    finally:
        # 关闭连接
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    if migrate_books():
        print("数据迁移成功")
    else:
        print("数据迁移失败")
