# -*- coding: utf-8 -*-

import sqlite3
import psycopg2

sqlite_conn = sqlite3.connect('.\\fe\\data\\book.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接到PostgreSQL
pg_conn = psycopg2.connect('postgresql://postgres:0524@localhost:5432/bookstore')
pg_cursor = pg_conn.cursor()

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

# 查询 SQLite 数据库中的书籍信息
sqlite_cursor.execute("SELECT * FROM book")
book_records = sqlite_cursor.fetchall()

# 将书籍信息插入到 PostgreSQL 中
for i, record in enumerate(book_records):
    pg_cursor.execute("""
        INSERT INTO book (id, title, author, publisher, original_title, translator, 
        pub_year, pages, price, currency_unit, binding, isbn, author_intro, 
        book_intro, content, tags, picture)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        record[0], record[1], record[2], record[3], record[4], record[5],
        record[6], record[7], record[8], record[9], record[10], record[11],
        record[12], record[13], record[14], record[15], record[16]
    ))

# 提交更改
pg_conn.commit()

# 关闭数据库连接
sqlite_conn.close()
pg_conn.close()
