# services/services_set/user_service.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from services.permissions import IsAdminGroup
from user.functions.user import UserService

class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def list(self, request):
        return Response(UserService.list_users())

    def retrieve(self, request, pk=None):
        return Response(UserService.get_user(int(pk)))

    def create(self, request):
        # admin only
        for p in [IsAdminGroup()]:
            if not p.has_permission(request, self):
                return Response({"detail": p.message}, status=403)
        user = UserService.create_user(dict(request.data))
        return Response(user, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # ให้ staff/admin อัปเดตได้ขึ้นกับ DjangoModelPermissions อยู่แล้ว
        user = UserService.update_user(int(pk), dict(request.data))
        return Response(user)

    def destroy(self, request, pk=None):
        # admin only
        for p in [IsAdminGroup()]:
            if not p.has_permission(request, self):
                return Response({"detail": p.message}, status=403)
        UserService.delete_user(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
