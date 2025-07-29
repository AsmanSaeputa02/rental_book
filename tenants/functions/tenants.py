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
        primary_domain = f"{tenant.schema_name}.localhost"
        Domain.objects.get_or_create(
            domain=primary_domain,
            tenant=tenant,
            defaults={"is_primary": True}
        )

        # ➤ เพิ่ม domain 127.0.0.1 สำหรับ dev (เฉพาะถ้ายังไม่มี)
        existing_domain = Domain.objects.filter(domain="127.0.0.1").first()
        if not existing_domain:
            Domain.objects.create(
                domain="127.0.0.1",
                tenant=tenant,
                is_primary=False
            )
        elif existing_domain.tenant != tenant:
            print(f"⚠️ Domain '127.0.0.1' ถูกใช้โดย tenant อื่นแล้ว → ข้าม")

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

        return tenant
