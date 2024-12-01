from urllib.parse import urljoin
import requests
from fe import conf


def search_in_store(store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
    json = {
            'store_id': store_id,
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'content': content,
            'tags': tags,
            'book_intro': book_intro,
            'page': page,
            "per_page": per_page
    }
    url = urljoin(urljoin(conf.URL, "search/"), "search_in_store")
    r = requests.post(url, json=json)
    return r.status_code, r.json()


def search_all(title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
    json = {
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'content': content,
            'tags': tags,
            'book_intro': book_intro,
            'page': page,
            "per_page": per_page
    }
    url = urljoin(urljoin(conf.URL, "search/"), "search_all")
    r = requests.post(url, json=json)
    return r.status_code, r.json()