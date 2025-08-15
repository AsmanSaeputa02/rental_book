# services/views_admin.py (หรือไฟล์ที่ประกาศ endpoint นี้)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django_tenants.utils import schema_context, get_tenant_model
from book.functions import book

class CreateBookInTenantView(APIView):
    permission_classes = [permissions.IsAdminUser]  # หรือของคุณเอง

    def post(self, request, *args, **kwargs):
        schema_name = request.data.get("schema_name")
        data = request.data.get("data", {})

        if not schema_name:
            return Response({"detail": "schema_name is required"}, status=400)

        # ยืนยันว่า tenant มีจริง (ป้องกัน schema ผิด)
        Tenant = get_tenant_model()
        try:
            tenant = Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist:
            return Response({"detail": f"Unknown tenant schema: {schema_name}"}, status=404)

        # สลับเข้า schema ของ tenant แล้วค่อยสร้าง Book
        with schema_context(tenant.schema_name):
            ser = book(data=data)
            if ser.is_valid():
                obj = ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
