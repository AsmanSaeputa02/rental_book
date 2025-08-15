# book/functions/book.py
from typing import Dict, Any, List, Optional
from django.db import transaction
from django_tenants.utils import schema_context
from book.models import Book

# อนุญาตชื่อที่ API จะรับ แล้วเราจะ map ให้ตรงกับโมเดลจริงอีกชั้น
BOOK_WRITABLE_FIELDS = {"title", "author", "isbn", "available_count"}

# ช่วยหา “ชื่อฟิลด์จริง” ของจำนวนคงเหลือในโมเดล (รองรับหลายชื่อที่พบบ่อย)
CANDIDATE_AVAILABLE_FIELDS = ["available_count", "available_copies", "available", "stock", "quantity"]

def _resolve_available_field_name() -> Optional[str]:
    names = {f.name for f in Book._meta.get_fields()}
    for n in CANDIDATE_AVAILABLE_FIELDS:
        if n in names:
            return n
    return None

def _coerce_payload_to_model(payload: Dict[str, Any]) -> Dict[str, Any]:
    """map 'available_count' จาก API ไปเป็นชื่อฟิลด์จริงในโมเดล ถ้าจำเป็น"""
    data = dict(payload)
    model_field = _resolve_available_field_name()
    if model_field and "available_count" in data and model_field != "available_count":
        # ย้ายค่าไปฟิลด์จริง
        data[model_field] = data.pop("available_count")
    # ตัดคีย์ที่ไม่อยู่ในโมเดลทิ้ง (กันหลุด)
    model_fields = {f.name for f in Book._meta.get_fields()}
    return {k: v for (k, v) in data.items() if k in model_fields}

def _to_dict(obj: Book) -> Dict[str, Any]:
    # อ่านจำนวนคงเหลือจากชื่อที่มีจริง
    avail_field = _resolve_available_field_name()
    return {
        "id": obj.id,
        "title": getattr(obj, "title", None),
        "author": getattr(obj, "author", None),
        "isbn": getattr(obj, "isbn", None),
        "available_count": getattr(obj, avail_field, None) if avail_field else None,
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
        payload = _coerce_payload_to_model(payload)
        obj = Book.objects.create(**payload)
        return _to_dict(obj)

    # ---------- สำหรับ superadmin: ระบุ schema ----------
    @staticmethod
    @transaction.atomic
    def admin_create_book_in_schema(schema_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {k: v for k, v in data.items() if k in BOOK_WRITABLE_FIELDS}
        with schema_context(schema_name):
            payload = _coerce_payload_to_model(payload)
            obj = Book.objects.create(**payload)
            return _to_dict(obj)
