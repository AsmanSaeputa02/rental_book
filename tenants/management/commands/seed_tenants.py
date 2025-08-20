# tenants/management/commands/seed_tenants.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django_tenants.utils import (
    get_tenant_model,
    get_tenant_domain_model,
    schema_context,
)
from pathlib import Path
import json

class Command(BaseCommand):
    help = (
        "Seed tenants from tenants/data/tenants.json "
        "(create/update Client + Domain + migrate schema + seed groups + create/update Company in tenant)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="tenants/data/tenants.json",
            help="Path to tenants.json (default: tenants/data/tenants.json)",
        )

    def handle(self, *args, **kwargs):
        json_path = Path(kwargs["file"]).resolve()
        if not json_path.exists():
            raise SystemExit(f"JSON file not found: {json_path}")

        raw = json.loads(json_path.read_text(encoding="utf-8"))
        # รองรับทั้ง 2 ฟอร์แมต: [{"schema_name":...}, ...] หรือ {"tenants":[...]}
        tenants = raw if isinstance(raw, list) else raw.get("tenants", [])
        if not isinstance(tenants, list) or not tenants:
            self.stdout.write(self.style.WARNING("No tenants to seed."))
            return

        Tenant = get_tenant_model()
        Domain = get_tenant_domain_model()

        for item in tenants:
            schema = item["schema_name"].strip()
            if schema == "public":
                self.stdout.write(self.style.WARNING("Skip 'public' (reserved schema)."))
                continue

            name = item.get("name", schema)
            paid_until = item.get("paid_until", None)
            on_trial = bool(item.get("on_trial", False))
            # กำหนดโดเมน (อนุญาต override ผ่าน JSON: "domain": "...") — ถ้าไม่ใส่จะใช้ <schema-with-dash>.localhost
            domain_name = item.get("domain") or f"{schema.replace('_','-')}.localhost"

            # 1) สร้าง/อัปเดต Client (public schema)
            tenant, created = Tenant.objects.get_or_create(
                schema_name=schema,
                defaults={"name": name, "paid_until": paid_until, "on_trial": on_trial},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"[{schema}] created Client"))
            else:
                # อัปเดตให้ตรง JSON (idempotent)
                changed = []
                if tenant.name != name:
                    tenant.name = name
                    changed.append("name")
                if paid_until is not None and tenant.paid_until != paid_until:
                    tenant.paid_until = paid_until
                    changed.append("paid_until")
                if tenant.on_trial != on_trial:
                    tenant.on_trial = on_trial
                    changed.append("on_trial")
                if changed:
                    tenant.save()
                    self.stdout.write(self.style.NOTICE(f"[{schema}] updated Client fields: {', '.join(changed)}"))
                else:
                    self.stdout.write(self.style.NOTICE(f"[{schema}] Client already up-to-date"))

            # 2) Domain primary
            d, d_created = Domain.objects.get_or_create(
                domain=domain_name, tenant=tenant, defaults={"is_primary": True}
            )
            if d_created:
                self.stdout.write(f"  - domain created: {d.domain} (primary)")
            else:
                if not d.is_primary:
                    d.is_primary = True
                    d.save()
                    self.stdout.write(f"  - domain set primary: {d.domain}")
                else:
                    self.stdout.write(f"  - domain exists: {d.domain} (primary)")

            # ให้แต่ละ tenant มี primary เพียงตัวเดียว
            Domain.objects.filter(tenant=tenant).exclude(pk=d.pk).update(is_primary=False)

            # 3) migrate เฉพาะสคีมานี้ (เร็วและชัด)
            call_command("migrate_schemas", schema=schema, interactive=False, verbosity=0)
            self.stdout.write("  - migrated")

            # 4) seed groups/permissions (admin/staff) ใน tenant นี้
            try:
                call_command("seed_groups", schema=schema, verbosity=0)
                self.stdout.write("  - seeded groups (admin/staff)")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  - seed_groups skipped/failed: {e}"))

            # 5) สร้าง/อัปเดต Company ภายในสคีมาของ tenant
            company_payload = item.get("company") or {}
            if company_payload:
                try:
                    from company.models import Company  # import หลัง migrate แน่ใจว่า model พร้อม
                    with schema_context(schema):
                        cid = company_payload.get("cid")
                        if not cid:
                            # ใช้ schema เป็น cid fallback
                            cid = f"{schema}-cid"

                        defaults = {
                            "name": company_payload.get("name", name),
                            "alias": company_payload.get("alias", name),
                            "client_id": company_payload.get("client_id", ""),
                            "client_secret": company_payload.get("client_secret", ""),
                            "is_active": bool(company_payload.get("is_active", True)),
                        }
                        Company.objects.update_or_create(cid=cid, defaults=defaults)
                        self.stdout.write("  - company upserted")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  - company upsert skipped/failed: {e}"))

            self.stdout.write(self.style.SUCCESS(f"[{schema}] done"))

        self.stdout.write(self.style.SUCCESS("All tenants seeded successfully."))
