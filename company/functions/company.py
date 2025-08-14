# company/functions/company.py
from typing import Dict, Any, List, Optional, Union
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from company.models import Company

# ฟิลด์ที่อนุญาตให้แก้ไขได้
WRITABLE_FIELDS = {
    "name",
    "contact_email",
    "phone",
    "address",
    "tax_id",
}
REQUIRED_ON_CREATE = {"name"}  # ระบุฟิลด์บังคับตอน create

def _to_dict(obj: Company) -> Dict[str, Any]:
    return {
        # รองรับทั้งโครงที่มี cid และไม่มี
        "id": getattr(obj, "id", None),
        "cid": getattr(obj, "cid", None),
        "name": getattr(obj, "name", None),
        "contact_email": getattr(obj, "contact_email", None),
        "phone": getattr(obj, "phone", None),
        "address": getattr(obj, "address", None),
        "tax_id": getattr(obj, "tax_id", None),
        "created_at": getattr(obj, "created_at", None),
        "updated_at": getattr(obj, "updated_at", None),
    }

def _get_company_obj(identifier: Union[str, int]) -> Company:
    """
    ดึง Company โดยพยายามใช้ cid ก่อน ถ้าไม่เจอ/ไม่มี ใช้ pk (id)
    """
    # cid เป็นสตริง (เช่น uuid/รหัสกำหนดเอง)
    if isinstance(identifier, str):
        try:
            return Company.objects.get(cid=identifier)
        except (Company.DoesNotExist, Company.MultipleObjectsReturned):
            pass
    # ตกมาใช้ id (pk)
    return Company.objects.get(pk=identifier)

class CompanyService:
    @staticmethod
    def create_company(data: Dict[str, Any]) -> Dict[str, Any]:
        missing = REQUIRED_ON_CREATE - set(data.keys())
        if missing:
            raise ValidationError({"missing_fields": sorted(missing)})

        payload = {k: v for k, v in data.items() if k in (WRITABLE_FIELDS | {"cid"})}
        obj = Company.objects.create(**payload)
        return _to_dict(obj)

    @staticmethod
    def list_companies(limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        qs = Company.objects.all().order_by("-id")
        if limit is not None:
            qs = qs[offset : offset + limit]
        return [_to_dict(o) for o in qs]

    @staticmethod
    def get_company(identifier: Union[str, int]) -> Dict[str, Any]:
        obj = _get_company_obj(identifier)
        return _to_dict(obj)

    @staticmethod
    @transaction.atomic
    def update_company(identifier: Union[str, int], data: Dict[str, Any]) -> Dict[str, Any]:
        obj = _get_company_obj(identifier)
        # ล็อกแถวกัน race
        obj = Company.objects.select_for_update().get(pk=obj.pk)

        for k, v in data.items():
            if k in WRITABLE_FIELDS:
                setattr(obj, k, v)
        obj.full_clean(exclude={"cid"})  # กันข้อมูลผิดรูป
        obj.save()
        return _to_dict(obj)

    @staticmethod
    @transaction.atomic
    def delete_company(identifier: Union[str, int]) -> Dict[str, Any]:
        obj = _get_company_obj(identifier)
        pk_or_cid = getattr(obj, "cid", obj.pk)
        obj.delete()
        return {"deleted": True, "id": getattr(obj, "id", None), "cid": getattr(obj, "cid", None), "key": pk_or_cid}
