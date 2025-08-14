from typing import Dict, Any, List, Optional
from django.db import transaction
from django_tenants.utils import schema_context
from book.models import Book

BOOK_WRITABLE_FIELDS = {"title", "author", "isbn", "available_count"}

def _to_dict(obj: Book) -> Dict[str, Any]:
    return {
        "id": obj.id,
        "title": getattr(obj, "title", None),
        "author": getattr(obj, "author", None),
        "isbn": getattr(obj, "isbn", None),
        "available_count": getattr(obj, "available_count", None),
        "created_at": getattr(obj, "created_at", None),
        "updated_at": getattr(obj, "updated_at", None),
    }

class BookService:
    # ---------- ใช้ใน tenant ปัจจุบัน ----------
    @staticmethod
    def list_books(limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        qs = Book.objects.all().order_by("-id")
        if limit is not None:
            qs = qs[offset:offset + limit]
        return [_to_dict(b) for b in qs]

    @staticmethod
    @transaction.atomic
    def create_book(data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {k: v for k, v in data.items() if k in BOOK_WRITABLE_FIELDS}
        obj = Book.objects.create(**payload)
        return _to_dict(obj)

    # ---------- สำหรับ superadmin: ระบุ schema ----------
    @staticmethod
    @transaction.atomic
    def admin_create_book_in_schema(schema_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {k: v for k, v in data.items() if k in BOOK_WRITABLE_FIELDS}
        with schema_context(schema_name):
            obj = Book.objects.create(**payload)
            return _to_dict(obj)
