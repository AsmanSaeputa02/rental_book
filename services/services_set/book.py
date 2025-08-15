from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from services.permissions import IsAdminGroup, ReadOnly
from book.functions.book import BookService
from book.models import Book
from book.functions import book


class BookViewSet(ViewSet):
    """
    จัดการ Book ใน 'tenant ปัจจุบัน' (เลือกจาก Host)
    - อ่าน: ใครก็ตามที่ล็อกอิน (และมี view_book) ใช้ได้
    - สร้าง: admin group เท่านั้น
    """
    # ถ้าอยากใช้ rule: อ่านได้ทุกคน / เขียนได้เฉพาะ admin
    # permission_classes = [IsAuthenticated, (ReadOnly | IsAdminGroup)]
    # ถ้าจะพึ่ง DjangoModelPermissions สำหรับ view/add/change ก็ใช้แบบบรรทัดล่าง:
    queryset = Book.objects.all()               # ✅ สำคัญ
    serializer_class = book
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def list(self, request):
        limit = request.query_params.get("limit")
        offset = request.query_params.get("offset", 0)
        limit = int(limit) if limit is not None else None
        offset = int(offset) if offset is not None else 0
        return Response(BookService.list_books(limit=limit, offset=offset))

    def create(self, request):
        # บังคับให้เฉพาะ admin group สร้างได้
        checker = IsAdminGroup()
        if not checker.has_permission(request, self):
            return Response({"detail": checker.message}, status=403)
        result = BookService.create_book(request.data)
        return Response(result, status=status.HTTP_201_CREATED)
