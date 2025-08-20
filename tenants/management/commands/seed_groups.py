from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context, get_tenant_model

# กำหนดสิทธิ์ต่อกลุ่ม (ต่อ "แอป" และ "action")
GROUP_PERMISSION_MAP = {
    "admin": {
        "book":     ["add", "change", "delete", "view"],
        "rental":   ["add", "change", "delete", "view"],
        "company":  ["add", "change", "delete", "view"],
        "user":     ["add", "change", "delete", "view"],
    },
    "staff": {
        "book":     ["view"],
        "rental":   ["add", "change", "view"],
        "user":     ["view"],
    },
}

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
        cts = ContentType.objects.filter(app_label=app_label)
        if not cts.exists():
            continue
        for ct in cts:
            model_name = ct.model
            for action in actions:
                codename = f"{action}_{model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    desired.add(perm)
                except Permission.DoesNotExist:
                    continue
    return desired


class Command(BaseCommand):
    help = "Seed groups & permissions for each tenant schema (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            help="Specify tenant schema name (e.g. branch-a)",
        )

    def handle(self, *args, **options):
        schema = options.get("schema")

        if schema:
            with schema_context(schema):
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f"[{schema}] Seeding groups & permissions ..."
                ))
                self.seed_groups_and_permissions()
                self.stdout.write(self.style.SUCCESS(f"[{schema}] Done."))
        else:
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
                    self.seed_groups_and_permissions()
                    self.stdout.write(self.style.SUCCESS(f"[{tenant.schema_name}] Done."))

        self.stdout.write(self.style.SUCCESS("All tenants updated."))

    def seed_groups_and_permissions(self):
        for group_name, app_perms in GROUP_PERMISSION_MAP.items():
            group, _created = Group.objects.get_or_create(name=group_name)
            desired = desired_permissions_for_schema(app_perms)
            group.permissions.set(desired)
            group.save()
            self.stdout.write(f"  - Group '{group_name}': {len(desired)} perms")
