from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_tenant_model
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Seed test admin users (admin@demo.com) for each tenant"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        TenantModel = get_tenant_model()
        tenants = TenantModel.objects.exclude(schema_name="public")

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                user, created = User.objects.get_or_create(email="admin@demo.com")
                user.is_active = True
                user.is_staff = True
                user.set_password("12345678")
                user.save()

                admin_group, _ = Group.objects.get_or_create(name="admin")
                user.groups.add(admin_group)

                self.stdout.write(self.style.SUCCESS(
                    f"{'✅ Created' if created else '🔁 Updated'} admin@demo.com in {tenant.schema_name}"
                ))
