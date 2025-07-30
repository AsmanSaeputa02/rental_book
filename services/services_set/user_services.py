# 📁 services/services_set/user_service.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from user.functions.user import UserService

class UserViewSet(ViewSet):
    def list(self, request):
        users = UserService.list_users()
        return Response([{"id": u.id, "email": u.email, "name": u.full_name} for u in users])

    def retrieve(self, request, pk=None):
        user = UserService.get_user(pk)
        return Response({"id": user.id, "email": user.email, "name": user.full_name})

    def create(self, request):
        data = request.data
        user = UserService.create_user(data)
        return Response({"id": user.id, "email": user.email, "name": user.full_name}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        data = request.data
        user = UserService.update_user(pk, data)
        return Response({"id": user.id, "email": user.email, "name": user.full_name})

    def destroy(self, request, pk=None):
        UserService.delete_user(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
