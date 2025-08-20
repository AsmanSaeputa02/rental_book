# services/services_set/admin_user_create.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class SuperadminCreateTenantUser(APIView):
    @swagger_auto_schema(
        operation_summary="Create user in tenant (Superadmin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password", "role"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="admin@branch-a.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, example="1234"),
                "full_name": openapi.Schema(type=openapi.TYPE_STRING, example="Admin User"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, enum=["admin", "staff"]),
            },
        ),
        responses={201: "Created", 403: "Forbidden"},
    )
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Only superadmin allowed"}, status=403)

        data = request.data
        role = data.get("role", "staff")
        user = User.objects.create_user(
            email=data["email"],
            password=data["password"],
            full_name=data.get("full_name", "")
        )
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        return Response({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": role,
        }, status=201)
