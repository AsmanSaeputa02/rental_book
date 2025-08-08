from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from django.db import connection




class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema

schema_view = get_schema_view(
    openapi.Info(title="SaaS Admin API", default_version="v1"),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)
def whoami(_):
    return HttpResponse(connection.schema_name)

def root_redirect(_):
    return HttpResponseRedirect(f"/{WEB_REAL_PATH}/admin/swagger/")

def ping(_):
    return HttpResponse("pong")

def hostinfo(request):
    return JsonResponse({
        "HTTP_HOST": request.META.get("HTTP_HOST"),
        "get_host": request.get_host(),
        "schema": connection.schema_name,
    })

WEB_REAL_PATH = getattr(settings, "WEB_REAL_PATH", "book_project").strip("/")
prefix = f"{WEB_REAL_PATH}/"

urlpatterns = [
    path("", root_redirect),
    path(f"{WEB_REAL_PATH}/ping/", ping),
    path(f"{WEB_REAL_PATH}/admin/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="admin-schema-swagger-ui"),
    path(f"{WEB_REAL_PATH}/admin/", admin.site.urls),
    path(f"{WEB_REAL_PATH}/", include("services.urls")),   # => /book_project/api/...
    path(f"{WEB_REAL_PATH}/whoami/", whoami),
    path(f"{WEB_REAL_PATH}/hostinfo/", hostinfo),
]
