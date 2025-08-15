# book/functions/book.py
from typing import Dict, Any, List, Optional
from django.db import transaction, models
from django_tenants.utils import schema_context
from book.models import Book

BOOK_WRITABLE_FIELDS = {"title", "author", "isbn", "available_count"}
CANDIDATE_AVAILABLE_FIELDS = ["available_count", "available_copies", "available", "stock", "quantity"]

# (ทางเลือก) cache ชื่อฟิลด์ไว้ ลด overhead
_AVAILABLE_FIELD_NAME: Optional[str] = None
def _resolve_available_field_name() -> Optional[str]:
    global _AVAILABLE_FIELD_NAME
    if _AVAILABLE_FIELD_NAME is not None:
        return _AVAILABLE_FIELD_NAME
    names = {f.name for f in Book._meta.get_fields()}
    for n in CANDIDATE_AVAILABLE_FIELDS:
        if n in names:
            _AVAILABLE_FIELD_NAME = n
            break
    return _AVAILABLE_FIELD_NAME

def _coerce_available_value_for_field(model_field: models.Field, value: Any) -> Any:
    # Boolean
    if isinstance(model_field, models.BooleanField):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            s = value.strip().lower()
            if s in {"true", "t", "yes", "y", "1"}:
                return True
            if s in {"false", "f", "no", "n", "0"}:
                return False
            # ถ้าเป็นตัวเลขในรูป string
            try:
                return bool(int(s))
            except Exception:
                pass
        # fallback ปล่อยให้ validation เตะ (จะได้ error ชัด)
        return value

    # Integer / PositiveInteger
    if isinstance(model_field, (models.IntegerField, models.PositiveIntegerField, models.SmallIntegerField, models.BigIntegerField)):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            return int(value.strip())  # อาจ raise ValueError ให้ DRF โยน 400
    return value  # อื่น ๆ ปล่อยไปตามเดิม

def _coerce_payload_to_model(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(payload)
    model_field_name = _resolve_available_field_name()
    if model_field_name and "available_count" in data and model_field_name != "available_count":
        data[model_field_name] = data.pop("available_count")

    # ตัดคีย์ที่ไม่มีในโมเดลทิ้ง
    model_fields = {f.name: f for f in Book._meta.get_fields() if isinstance(f, models.Field)}
    coerced: Dict[str, Any] = {}
    for k, v in data.items():
        if k in model_fields:
            # ถ้าเป็นฟิลด์จำนวน/สถานะ ให้ช่วยแปลงชนิด
            if k == model_field_name:
                coerced[k] = _coerce_available_value_for_field(model_fields[k], v)
            else:
                coerced[k] = v
    return coerced

def _to_dict(obj: Book) -> Dict[str, Any]:
    avail_field = _resolve_available_field_name()
    return {
        "id": obj.id,
        "title": getattr(obj, "title", None),
        "author": getattr(obj, "author", None),
        "isbn": getattr(obj, "isbn", None),
        # normalize ออกมาเป็น available_count เสมอ (จะได้ API คงรูป)
        "available_count": getattr(obj, avail_field, None) if avail_field else None,
        "created_at": getattr(obj, "created_at", None),
        "updated_at": getattr(obj, "updated_at", None),
    }

class BookService:
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

    @staticmethod
    @transaction.atomic
    def admin_create_book_in_schema(schema_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {k: v for k, v in data.items() if k in BOOK_WRITABLE_FIELDS}
        with schema_context(schema_name):
            payload = _coerce_payload_to_model(payload)
            obj = Book.objects.create(**payload)
            return _to_dict(obj)
