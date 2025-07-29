from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from company.functions.company import CompanyService
from django.core.exceptions import ObjectDoesNotExist


class CompanyViewSet(ViewSet):
    """
    ViewSet สำหรับจัดการ Company (Swagger Only)
    """

    def list(self, request):
        companies = CompanyService.list_companies()
        return Response([
            {
                "cid": c.cid,
                "name": c.name,
                "alias": c.alias,
                "client_id": c.client_id,
                "client_secret": c.client_secret,
                "is_active": c.is_active
            }
            for c in companies
        ])

    def retrieve(self, request, pk=None):
        company = CompanyService.get_company(cid=pk)
        if not company:
            return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "cid": company.cid,
            "name": company.name,
            "alias": company.alias,
            "client_id": company.client_id,
            "client_secret": company.client_secret,
            "is_active": company.is_active
        })

    def create(self, request):
        try:
            data = request.data
            company = CompanyService.create_company(data)
            return Response({
                "cid": company.cid,
                "name": company.name,
                "alias": company.alias,
                "client_id": company.client_id,
                "client_secret": company.client_secret,
                "is_active": company.is_active
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        data = request.data
        company = CompanyService.update_company(cid=pk, data=data)
        if not company:
            return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "cid": company.cid,
            "name": company.name,
            "alias": company.alias,
            "client_id": company.client_id,
            "client_secret": company.client_secret,
            "is_active": company.is_active
        })

    def destroy(self, request, pk=None):
        try:
            company = CompanyService.get_company(pk)
            if not company:
                return Response({"detail": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            company.delete()
            return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
