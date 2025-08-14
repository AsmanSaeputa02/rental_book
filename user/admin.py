# user/admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin

# ใช้ตัวแปร runtime สำหรับ Model จริง (ห้ามเอาไปเป็น type hint)
RuntimeUser = get_user_model()

class GroupMemberInline(admin.TabularInline):
    """สมาชิกของ Group (เชื่อมผ่าน m2m)"""
    model = RuntimeUser.groups.through
    extra = 0
    verbose_name = "member"
    verbose_name_plural = "members"
    autocomplete_fields = ("user",)

# --- Group admin ---

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    """
    - โชว์สิทธิ์แบบละเอียด (app | model | verbose name)
    - เพิ่มแท็บ members
    - ใช้ filter_horizontal ให้ย้ายสิทธิ์สะดวก
    """
    inlines = [GroupMemberInline]
    readonly_fields = ("permissions_verbose",)
    filter_horizontal = ("permissions",)

    fieldsets = (
        (None, {"fields": ("name", "permissions", "permissions_verbose")}),
    )

    # ตัด type hint 'obj: User' ออก เพื่อไม่ให้ Pylance ฟ้อง
    def permissions_verbose(self, obj):
        perms = obj.permissions.select_related("content_type").order_by(
            "content_type__app_label", "content_type__model", "codename"
        )
        lines = [f"{p.content_type.app_label} | {p.content_type.model} | {p.name}" for p in perms]
        return mark_safe("<br>".join(lines) or "—")
    permissions_verbose.short_description = "Chosen permissions (detailed)"

# --- User admin ---

try:
    admin.site.unregister(RuntimeUser)
except admin.sites.NotRegistered:
    pass

@admin.register(RuntimeUser)
class UserAdmin(BaseUserAdmin):
    """
    - list/search ตาม email
    - ช่อง readonly แสดงสิทธิ์ทั้งหมด
    - ปรับ add_fieldsets ให้สร้างผู้ใช้ใหม่จาก admin ได้ง่าย (email+password)
    """
    HAS_FULL_NAME = hasattr(RuntimeUser, "full_name")

    list_display = ("email", "full_name" if HAS_FULL_NAME else "id", "is_active", "is_staff")
    search_fields = ("email", "full_name" if HAS_FULL_NAME else "email")
    ordering = ("-id",)
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")

    readonly_fields = ("all_permissions_verbose",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": (("full_name",) if HAS_FULL_NAME else tuple())}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
        ("Computed", {"fields": ("all_permissions_verbose",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_superuser", "groups"),
        }),
    )

    # ตัด type hint 'obj: User' ออกเช่นกัน
    def all_permissions_verbose(self, obj):
        """รวมสิทธิ์ทั้งหมด (จากกลุ่ม + user_permissions) แสดงแบบอ่านง่าย"""
        if not obj or not obj.pk:
            return "—"
        codes = {perm.split(".", 1)[1] for perm in obj.get_all_permissions()}
        perms = Permission.objects.select_related("content_type").filter(
            codename__in=codes
        ).order_by("content_type__app_label", "content_type__model", "codename")
        lines = [f"{p.content_type.app_label} | {p.content_type.model} | {p.name}" for p in perms]
        return mark_safe("<br>".join(lines) or "—")
    all_permissions_verbose.short_description = "All permissions (via groups + direct)"
