import pytest

from fe.access import search
from fe.access import book
import random

class TestSearchBooksAll:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self, str_len=2):

        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, book_db.get_book_count())
        self.json = {
            "title": "",
            "author": "",
            "publisher": "",
            "isbn": "",
            "content": "",
            "tags": "",
            "book_intro": ""
        }
        selected_book = random.choice(self.books)
        for i in ['title', 'author', 'publisher', 'isbn', 'content', 'tags', 'book_intro']:
            if getattr(selected_book, i) is not None:
                text_length = len(getattr(selected_book, i))
                if random.random() > 0.8 and text_length >= str_len:
                    start_index = random.randint(0, text_length - 2)
                    self.json[i] = getattr(selected_book, i)[start_index:start_index + 2]
        yield

    def test_ok(self):
        def check_ok():
            processed_json = {}
            for key, value in self.json.items():
                if len(value) != 0 :
                    processed_json[key] = value
            print('pro',processed_json)
            if len(processed_json.keys()) == 0:
                return [book.id for book in self.books]

            res = []
            for d in self.books:
                flag = 0
                for key, substring in processed_json.items():
                    if getattr(d, key) is not None:
                        if getattr(d, key).find(substring) == -1:
                            flag=1
                    else:
                        flag=1
                if flag==0:
                    res.append(d.id)

            return res

        json_list = list(self.json.values())

        code, res = search.search_all(json_list[0], json_list[1], json_list[2], json_list[3], json_list[4],
                                         json_list[5], json_list[6],1,10000000)
        assert code == 200

        res = [i['id'] for i in res['data']]
        right_answer = check_ok()
        assert len(right_answer) == len(res)

        for i in res:
            if i not in right_answer:
                assert False  