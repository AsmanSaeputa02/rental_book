# tests/base.py

from django_tenants.test.cases import TenantTestCase
from tenants.models import Client, Domain
from django_tenants.utils import get_public_schema_name, schema_context

class BaseTenantTestCase(TenantTestCase):
    @classmethod
    def setUpClass(cls):
        # สร้าง tenant ใน public schema เท่านั้น
        with schema_context(get_public_schema_name()):
            cls.tenant, _ = Client.objects.get_or_create(
                schema_name="testschema",
                defaults={"name": "TestSchema"}
            )
            Domain.objects.get_or_create(
                domain="testschema.localhost",
                defaults={"tenant": cls.tenant, "is_primary": True}
            )
        # เรียก super เพื่อสลับไปที่ schema ‘testschema’ ให้ TestCase ทำงานต่อ
        super().setUpClass()
