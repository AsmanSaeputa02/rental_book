# tenants/functions/tenants.py

from tenants.models import Client, Domain
from django_tenants.utils import schema_context
from company.models import Company


class TenantService:
    @staticmethod
    def register_with_company(tenant_data):
        tenant, created = Client.objects.get_or_create(
            schema_name=tenant_data["schema_name"],
            defaults={
                "name": tenant_data["name"],
                "paid_until": tenant_data.get("paid_until"),
                "on_trial": tenant_data.get("on_trial", True),
            }
        )

        # ➤ สร้าง domain หลัก เช่น branch_a.localhost
        primary_domain = tenant_data.get("domain_url", f"{tenant.schema_name}.localhost")
        Domain.objects.get_or_create(
            domain=primary_domain,
            tenant=tenant,
            defaults={"is_primary": True}
        )

        # ➤ เพิ่ม domain 127.0.0.1 สำหรับ dev (ใช้ get_or_create แทน create)
        domain_127, domain_created = Domain.objects.get_or_create(
            domain="127.0.0.1",
            defaults={
                "tenant": tenant,
                "is_primary": False
            }
        )
        
        if domain_created:
            print(f"✅ เพิ่ม domain '127.0.0.1' ให้กับ tenant '{tenant.schema_name}' สำเร็จ")
        else:
            # ถ้า domain มีอยู่แล้ว แต่ tenant ต่างกัน อัปเดต tenant
            if domain_127.tenant != tenant:
                print(f"ℹ️ อัปเดต domain '127.0.0.1' จาก tenant '{domain_127.tenant.schema_name}' เป็น '{tenant.schema_name}'")
                domain_127.tenant = tenant
                domain_127.save()
            else:
                print(f"ℹ️ Domain '127.0.0.1' ถูกใช้กับ tenant '{tenant.schema_name}' อยู่แล้ว")

        # ➤ สร้าง Company เมื่อ tenant ถูกสร้างใหม่เท่านั้น
        if created:
            with schema_context(tenant.schema_name):
                company_info = tenant_data["company"]
                Company.objects.get_or_create(
                    cid=company_info["cid"],
                    defaults={
                        "name": company_info["name"],
                        "alias": company_info["alias"],
                        "client_id": company_info["client_id"],
                        "client_secret": company_info["client_secret"],
                        "is_active": company_info["is_active"],
                    }
                )

