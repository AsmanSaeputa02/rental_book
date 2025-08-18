# user/functions/user.py
from typing import Dict, Any, List
from django.contrib.auth import get_user_model
from django.db import transaction

UserModel = get_user_model()

class UserService:
    @staticmethod
    def list_users() -> List[dict]:
        return [
            {"id": u.id,
            "email": u.email, 
            "name": getattr(u, "full_name", "")}
            for u in UserModel.objects.all().order_by("-id")
        ]

    @staticmethod
    def get_user(user_id: int) -> dict:
        u = UserModel.objects.get(id=user_id)
        return {"id": u.id, "email": u.email, "name": getattr(u, "full_name", "")}

    @staticmethod
    @transaction.atomic
    def create_user(data: Dict[str, Any]) -> dict:
        password = data.pop("password", None)
        if not password:
            raise ValueError("password is required")
        u = UserModel.objects.create(**data)
        u.set_password(password)
        u.save()
        return {"id": u.id, "email": u.email, "name": getattr(u, "full_name", "")}

    @staticmethod
    @transaction.atomic
    def update_user(user_id: int, data: Dict[str, Any]) -> dict:
        u = UserModel.objects.get(id=user_id)

        password = data.pop("password", None)
        if password:
            u.set_password(password)

        for key, value in data.items():
            setattr(u, key, value)

        u.save()
        return {"id": u.id, "email": u.email, "name": getattr(u, "full_name", "")}

    @staticmethod
    @transaction.atomic
    def delete_user(user_id: int) -> None:
        UserModel.objects.filter(id=user_id).delete()
