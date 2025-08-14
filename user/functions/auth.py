# user/functions/auth.py
from typing import Dict, Any
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken

DEFAULT_SIGNUP_ROLE = "staff"

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> Dict[str, Any] | None:
        user = authenticate(username=email, password=password)
        if not user:
            return None
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "name": getattr(user, "full_name", ""),
        }

    @staticmethod
    def register(data: dict) -> Dict[str, Any]:
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name", "")
        role = data.get("role", DEFAULT_SIGNUP_ROLE)

        if not email or not password:
            raise ValidationError({"detail": "email and password are required"})

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "This email is already in use"})

        user = User.objects.create_user(email=email, password=password, full_name=full_name)

        try:
            g = Group.objects.get(name=role)
            user.groups.add(g)
        except Group.DoesNotExist:
            staff_group, _ = Group.objects.get_or_create(name=DEFAULT_SIGNUP_ROLE)
            user.groups.add(staff_group)

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "name": getattr(user, "full_name", ""),
            "role": role,
        }
