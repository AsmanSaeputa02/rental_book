# tenants/functions/admin_auth.py
from typing import Optional, Dict, Any
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django_tenants.utils import get_tenant_model

class AdminAuthService:
    @staticmethod
    def login(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        ล็อกอินด้วยบัญชีใน schema 'public' ที่เป็น superuser เท่านั้น
        และคืนรายการ tenants (ตัด 'public' ออก)
        """
        # หมายเหตุ: ถ้า USERNAME_FIELD ของคุณคือ 'email'
        # การเรียก authenticate(email=..., password=...) ใช้ได้
        user = authenticate(email=email, password=password)
        if not user or not user.is_superuser:
            return None

        refresh = RefreshToken.for_user(user)

        Tenant = get_tenant_model()
        tenants = (
            Tenant.objects.exclude(schema_name="public")
            .values("schema_name", "name")
            .order_by("schema_name")
        )

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"email": user.email, "name": getattr(user, "full_name", "") or ""},
            "tenants": list(tenants),  # ✅ ไม่มี 'public'
        }
