# 🔧 services/services_set/book_service.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from book.functions.book import BookService

class BookViewSet(ViewSet):
    """
    ViewSet สำหรับจัดการ Book (Swagger Only)
    """
    def list(self, request):
        return Response(BookService.list_books())
