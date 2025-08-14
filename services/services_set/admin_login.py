# services/services_set/admin_login.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tenants.functions.admin_auth import AdminAuthService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AdminLoginView(APIView):
    @swagger_auto_schema(
        operation_summary="Superadmin Login (Public Schema)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="superadmin@your.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, example="••••••"),
            },
        ),
        responses={200: "Login Success", 401: "Unauthorized"},
    )
    def post(self, request):
        data = request.data
        result = AdminAuthService.login(data.get("email"), data.get("password"))
        if result:
            return Response(result)
        return Response({"detail": "Invalid credentials or not superadmin"}, status=status.HTTP_401_UNAUTHORIZED)
