# services/services_set/auth_service.py
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from user.functions.auth import AuthService
from services.permissions import IsAdminGroup

class AuthViewSet(ViewSet):
    @swagger_auto_schema(
        method='post',
        operation_summary="Login (tenant)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="admin@branch-a.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, example="1234"),
            },
        ),
        responses={200: openapi.Response("JWT Token")}
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        data = request.data
        result = AuthService.login(data.get("email"), data.get("password"))
        if result:
            return Response(result)
        return Response({"error": "Invalid credentials"}, status=401)

    @swagger_auto_schema(
        method='post',
        operation_summary="Register user in this tenant (admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="new@branch-a.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, example="1234"),
                "full_name": openapi.Schema(type=openapi.TYPE_STRING, example="New User"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, enum=["admin", "staff"], default="staff"),
            },
        ),
        responses={201: openapi.Response("Created user and returned JWT")}
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsAdminGroup])
    def register(self, request):
        result = AuthService.register(request.data)
        return Response(result, status=201)
