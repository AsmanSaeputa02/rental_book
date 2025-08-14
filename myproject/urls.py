from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from django.db import connection
from django_tenants.utils import get_tenant, get_tenant_model, get_tenant_domain_model


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

def debug_tenant(request):
    try:
        current_tenant = get_tenant(request)
        tenant_model = get_tenant_model()
        domain_model = get_tenant_domain_model()
        
        # Get host from request
        host = request.get_host()
        http_host = request.META.get('HTTP_HOST', 'NOT SET')
        
        # Try to find domain - django-tenants strips port automatically
        search_host = host.split(':')[0]  # Remove port if present
        try:
            domain_obj = domain_model.objects.get(domain=search_host)
            matched_tenant = domain_obj.tenant
        except domain_model.DoesNotExist:
            domain_obj = None
            matched_tenant = None
        except Exception as e:
            domain_obj = f"Error: {e}"
            matched_tenant = None
        
        return JsonResponse({
            "request_host": host,
            "http_host": http_host,
            "search_host": search_host,
            "current_schema": connection.schema_name,
            "current_tenant": {
                "schema_name": current_tenant.schema_name if current_tenant else None,
                "id": current_tenant.id if current_tenant else None,
            },
            "domain_lookup": {
                "searched_for": search_host,
                "found_domain": domain_obj.domain if domain_obj and hasattr(domain_obj, 'domain') else str(domain_obj),
                "matched_tenant_schema": matched_tenant.schema_name if matched_tenant else None,
            },
            "all_domains": [
                {"domain": d.domain, "tenant": d.tenant.schema_name} 
                for d in domain_model.objects.all()
            ]
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)

WEB_REAL_PATH = getattr(settings, "WEB_REAL_PATH", "book_project").strip("/")
prefix = f"{WEB_REAL_PATH}/"

urlpatterns = [
    path("", root_redirect),
    path(f"{WEB_REAL_PATH}/ping/", ping),
    path(f"{WEB_REAL_PATH}/admin/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="admin-schema-swagger-ui"),
    path(f"{WEB_REAL_PATH}/admin/", admin.site.urls),
    path(f"{WEB_REAL_PATH}/", include("services.urls")),  
    path(f"{WEB_REAL_PATH}/whoami/", whoami),
    path(f"{WEB_REAL_PATH}/hostinfo/", hostinfo),
    path(f"{WEB_REAL_PATH}/debug-tenant/", debug_tenant),  # Add this line
]