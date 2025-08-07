# tenants/functions/admin_auth.py
from django.contrib.auth import authenticate
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from tenants.models import Client

class AdminAuthService:
    @staticmethod
    def login(email, password):
        user = authenticate(email=email, password=password)
        if user and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            tenants = Client.objects.all().values("schema_name", "name")
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"email": user.email, "name": user.full_name},
                "tenants": list(tenants)
            }
        return None
