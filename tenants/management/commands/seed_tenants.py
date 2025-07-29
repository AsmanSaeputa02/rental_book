# 🔧 tenants/management/commands/seed_tenants.py
from tenants.functions.tenants import TenantService
from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = "Seed tenants from JSON"

    def handle(self, *args, **kwargs):
        with open("tenants/data/tenants.json") as f:
            tenants = json.load(f)
            for tenant_data in tenants:
                TenantService.register_with_company(tenant_data)
