import pytest
from django.contrib.auth import get_user_model, models as auth_models
from django_tenants.utils import schema_context, get_tenant_model
from django.core.management import call_command

pytestmark = pytest.mark.django_db

def test_staff_cannot_delete_company():
    tenant = get_tenant_model().objects.exclude(schema_name="public").first()
    with schema_context(tenant.schema_name):
        call_command("seed_groups")
        User = get_user_model()
        staff = User.objects.create_user(email="staff@example.com", password="pass")
        staff_group = auth_models.Group.objects.get(name="staff")
        staff.groups.add(staff_group)
        assert not staff.has_perm("company.delete_company")

def test_admin_can_delete_company():
    tenant = get_tenant_model().objects.exclude(schema_name="public").first()
    with schema_context(tenant.schema_name):
        call_command("seed_groups")
        User = get_user_model()
        admin = User.objects.create_user(email="admin@example.com", password="pass")
        admin_group = auth_models.Group.objects.get(name="admin")
        admin.groups.add(admin_group)
        assert admin.has_perm("company.delete_company")
