# services/services_set/book_admin.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from services.permissions import IsSuperAdmin
from book.functions.book import BOOK_WRITABLE_FIELDS, BookService
from django_tenants.utils import get_tenant_model

class AdminBookCreateView(APIView):
    """
    สร้างหนังสือเข้า tenant ที่ระบุ (เฉพาะ superadmin บน public schema)
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @swagger_auto_schema(
        operation_summary="Superadmin: Create book in a given tenant schema",
        security=[{"Bearer": []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["schema_name", "data"],
            properties={
                "schema_name": openapi.Schema(type=openapi.TYPE_STRING, example="branch_b"),
                "data": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "title": openapi.Schema(type=openapi.TYPE_STRING, example="Clean Code"),
                        "author": openapi.Schema(type=openapi.TYPE_STRING, example="Robert C. Martin"),
                        "isbn": openapi.Schema(type=openapi.TYPE_STRING, example="9780132350884"),
                        "available_count": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                    },
                ),
            },
        ),
        responses={201: "Created", 403: "Forbidden", 400: "Bad Request", 404: "Tenant Not Found"},
    )
    def post(self, request):
        schema_name = (request.data.get("schema_name") or "").strip()
        payload = request.data.get("data") or {}

        if not schema_name:
            return Response({"detail": "schema_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(payload, dict) or not payload:
            return Response({"detail": "data must be a non-empty object"}, status=status.HTTP_400_BAD_REQUEST)

        Tenant = get_tenant_model()
        if not Tenant.objects.filter(schema_name=schema_name).exists():
            return Response({"detail": f"schema '{schema_name}' not found"}, status=status.HTTP_404_NOT_FOUND)

        unknown = sorted(set(payload.keys()) - BOOK_WRITABLE_FIELDS)
        if unknown:
            return Response(
                {"detail": "unknown fields", "fields": unknown, "allowed": sorted(BOOK_WRITABLE_FIELDS)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = BookService.admin_create_book_in_schema(schema_name, payload)
        return Response(result, status=status.HTTP_201_CREATED)
