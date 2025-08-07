# tests/base.py

from django_tenants.test.cases import TenantTestCase
from tenants.models import Client, Domain
import datetime

class BaseTenantTestCase(TenantTestCase):

    @classmethod
    def setUpTestData(cls):
        # 👇 สร้าง tenant และ domain
        cls.tenant = Client.objects.create(
            schema_name="testschema",
            name="Test Tenant",
            paid_until=datetime.date(2030, 1, 1),
            on_trial=True,
        )
        Domain.objects.create(
            domain="testschema.localhost",
            tenant=cls.tenant,
            is_primary=True,
        )

    @classmethod
    def setup_tenant(cls, tenant):
        # 👇 ให้ TenantTestCase ใช้ tenant ที่เราสร้างไว้
        cls.tenant = tenant

    def setUp(self):
        super().setUp()
        from django.db import connection
        print("✅ CURRENT SCHEMA (AFTER activate):", connection.schema_name)
