# services/services_set/company.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from services.permissions import IsAdminGroup
from company.functions.company import CompanyService

class CompanyViewSet(viewsets.ViewSet):
    """
    Swagger-only ViewSet: ไม่มี business logic
    - ใช้ DjangoModelPermissions เป็นฐาน (map จากกลุ่ม/permissions)
    - destroy (ลบ) บังคับกลุ่ม admin เท่านั้น
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsAdminGroup()]
        return super().get_permissions()

    def list(self, request):  
        limit = request.query_params.get("limit")
        offset = request.query_params.get("offset", 0)
        limit = int(limit) if limit is not None else None
        offset = int(offset) if offset is not None else 0
        data = CompanyService.list_companies(limit=limit, offset=offset)
        return Response(data)

    def create(self, request):
        result = CompanyService.create_company(request.data)
        return Response(result, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        # pk อาจเป็น cid หรือ id
        data = CompanyService.get_company(pk)
        return Response(data)

    def update(self, request, pk=None):
        result = CompanyService.update_company(pk, request.data)
        return Response(result)

    def destroy(self, request, pk=None):
        result = CompanyService.delete_company(pk)
        return Response(result, status=status.HTTP_200_OK)
