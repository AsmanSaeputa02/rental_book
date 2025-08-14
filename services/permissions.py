from rest_framework.permissions import BasePermission, SAFE_METHODS
from django_tenants.utils import get_tenant

class IsAdminGroup(BasePermission):
    message = "Admin group only."
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.groups.filter(name="admin").exists())

class IsStaffGroup(BasePermission):
    message = "Staff group only."
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.groups.filter(name="staff").exists())

class IsAdminOrStaff(BasePermission):
    message = "Admin or Staff required."
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.groups.filter(name__in=["admin", "staff"]).exists())

class IsSuperAdmin(BasePermission):
    message = "Superadmin (public schema) only."
    def has_permission(self, request, view):
        u = request.user
        t = get_tenant()
        return bool(u and u.is_authenticated and u.is_superuser and t.schema_name == "public")

class ReadOnly(BasePermission):
    """อนุญาตเฉพาะเมธอดอ่าน (GET/HEAD/OPTIONS)"""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
