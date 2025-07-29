# 🔧 book/book/functions/book.py
from book.models import Book

class BookService:
    @staticmethod
    def list_books():
        return list(Book.objects.values())

    @staticmethod
    def create_book(data: dict):
        return Book.objects.create(**data)
