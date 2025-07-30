from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from user.models import User


class AuthService:
    @staticmethod
    def login(email, password):
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "email": user.email,
                "name": user.full_name,
            }
        return None
    @staticmethod
    def register(data: dict):
        user = User.objects.create_user(
            email=data["email"],
            password=data["password"],
            full_name=data.get("full_name", "")
        )
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "name": user.full_name,
        }
