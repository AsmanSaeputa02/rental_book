# services/services_set/user_service.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from services.permissions import IsAdminGroup
from user.functions.user import UserService

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(ViewSet):
    queryset = User.objects.all() 
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def list(self, request):
        return Response(UserService.list_users())

    def retrieve(self, request, pk=None):
        return Response(UserService.get_user(int(pk)))

    @swagger_auto_schema(
    operation_description="Create user (admin only)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "password"],
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, example="user@example.com"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, example="12345678"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, example="John Doe"),
        },
    )
    )
    def create(self, request):
        for p in [IsAdminGroup()]:
            if not p.has_permission(request, self):
                return Response({"detail": p.message}, status=403)
        user = UserService.create_user(dict(request.data))
        return Response(user, status=status.HTTP_201_CREATED)



    @swagger_auto_schema(
    operation_description="Update user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, example="New Name"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, example="newpass123"),
        },
    )
)
    def update(self, request, pk=None):
        user = UserService.update_user(int(pk), dict(request.data))
        return Response(user)


    def destroy(self, request, pk=None):
        # admin only
        for p in [IsAdminGroup()]:
            if not p.has_permission(request, self):
                return Response({"detail": p.message}, status=403)
        UserService.delete_user(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
