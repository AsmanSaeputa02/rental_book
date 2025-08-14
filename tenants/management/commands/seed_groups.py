# tenants/management/commands/seed_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context, get_tenant_model

# กำหนดสิทธิ์ต่อกลุ่ม (ต่อ "แอป" และ "action")
# หมายเหตุ: codename จะอยู่ในรูป "<action>_<modelname-lower>"
# เช่น add_book, change_rental, delete_company, view_user
GROUP_PERMISSION_MAP = {
    "admin": {
        "book":     ["add", "change", "delete", "view"],
        "rental":   ["add", "change", "delete", "view"],
        "company":  ["add", "change", "delete", "view"],
        "user":     ["add", "change", "delete", "view"],
    },
    "staff": {
        "book":     ["view"],                     # อ่านข้อมูลหนังสือ
        "rental":   ["add", "change", "view"],    # เปิด/อัปเดตการเช่า + ดู
        "company":  ["view"],                     # ดูข้อมูลบริษัท
        "user":     ["view"],                     # ดูรายชื่อลูกค้า/ผู้ใช้ (ถ้าจำเป็น)
    },
}

# หากมีโมเดลชื่อจริงไม่ตรง app_label/โมเดลดีฟอลต์
# สามารถ map เฉพาะเจาะจงเพิ่มได้ เช่น:
# MODEL_NAME_MAP = {"user": "user"}  # ปกติเป็นชื่อโมเดลตัวพิมพ์เล็ก
MODEL_NAME_MAP = {
    "book": "book",
    "rental": "rental",
    "company": "company",
    "user": "user",
}

def desired_permissions_for_schema(app_label_to_actions):
    """
    แปลง GROUP_PERMISSION_MAP เป็นเซ็ตของ Permission objects ตาม contenttypes จริงใน schema ปัจจุบัน
    """
    desired = set()
    for app_label, actions in app_label_to_actions.items():
        # หา content types ของแอปนั้น ๆ
        cts = ContentType.objects.filter(app_label=app_label)
        if not cts.exists():
            continue
        # วนทุก content type ในแอปนั้น (รองรับหลายโมเดลในแอป)
        for ct in cts:
            model_name = ct.model  # ชื่อโมเดลตัวพิมพ์เล็ก เช่น "book"
            for action in actions:
                codename = f"{action}_{model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    desired.add(perm)
                except Permission.DoesNotExist:
                    # ข้ามกรณี permission ยังไม่ถูกสร้าง (เช่นยังไม่มี migration)
                    continue
    return desired


class Command(BaseCommand):
    help = "Seed groups & permissions for each tenant schema (idempotent)."

    def handle(self, *args, **options):
        TenantModel = get_tenant_model()
        tenants = TenantModel.objects.exclude(schema_name="public")

        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenant found. Create tenants first."))
            return

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f"[{tenant.schema_name}] Seeding groups & permissions ..."
                ))

                for group_name, app_perms in GROUP_PERMISSION_MAP.items():
                    group, _created = Group.objects.get_or_create(name=group_name)

                    # สร้างชุด permission ที่อยากได้
                    desired = desired_permissions_for_schema(app_perms)

                    # ตั้ง permissions ให้ตรงเป๊ะ (idempotent)
                    group.permissions.set(desired)
                    group.save()

                    self.stdout.write(
                        f"  - Group '{group_name}': {len(desired)} perms"
                    )

                self.stdout.write(self.style.SUCCESS(
                    f"[{tenant.schema_name}] Done."
                ))

        self.stdout.write(self.style.SUCCESS("All tenants updated."))
