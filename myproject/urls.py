from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from django.shortcuts import redirect

# fallback ถ้า settings ไม่มี WEB_REAL_PATH
_real_path = getattr(settings, "WEB_REAL_PATH", "")

class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema

tenant_schema_view = get_schema_view(
    openapi.Info(
        title="SaaS Service API",
        default_version="v1",
        description="Book Rental SaaS API",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="SaaS License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

admin_schema_view = get_schema_view(
    openapi.Info(
        title="SaaS Admin API",
        default_version="v1",
        description="Book Rental SaaS Admin API",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="SaaS License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", lambda request: redirect(f"{_real_path}/admin/swagger/")),
    path(f"{_real_path}/services/", include("services.urls")),
    path(f"{_real_path}/admin/swagger/", admin_schema_view.with_ui("swagger", cache_timeout=0), name="admin-schema-swagger-ui"),
    path(f"{_real_path}/admin/redoc/", admin_schema_view.with_ui("redoc", cache_timeout=0), name="admin-schema-redoc"),
    path(f"{_real_path}/admin/", admin.site.urls),
    path(f"{_real_path}/accounts/", include("django.contrib.auth.urls")),
   
]
