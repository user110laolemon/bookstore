from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import search

bp_book = Blueprint("search", __name__, url_prefix="/search")


@bp_book.route("/search_in_store", methods=["POST"])
def search_in_store():

    store_id = request.json.get("store_id", "")
    title = request.json.get("title", "")
    author = request.json.get("author", "")
    publisher = request.json.get("publisher", "")
    isbn = request.json.get("isbn", "")
    content = request.json.get("content", "")
    tags = request.json.get("tags", "")
    book_intro = request.json.get("book_intro", "")
    page= int(request.json.get("page", ""))
    per_page = int(request.json.get("per_page", ""))

    u = search.Search()
    code, data = u.search_in_store(
        store_id,title,author,publisher,isbn,content,tags,book_intro,page,per_page
    )
    return jsonify({"data": data}), code

@bp_book.route("/search_all", methods=["POST"])
def search_all():
    title = request.json.get("title", "")
    author = request.json.get("author", "")
    publisher = request.json.get("publisher", "")
    isbn = request.json.get("isbn", "")
    content = request.json.get("content", "")
    tags = request.json.get("tags", "")
    book_intro = request.json.get("book_intro", "")
    page= int(request.json.get("page", ""))
    per_page = int(request.json.get("per_page", ""))

    u = search.Search()
    code, data = u.search_all(
        title,author,publisher,isbn,content,tags,book_intro,page,per_page
    )
    return jsonify({"data": data}), code
