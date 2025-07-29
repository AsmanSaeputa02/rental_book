from django.urls import path, include
from . import views
from services.services_set import company_sevice
from rest_framework.routers import DefaultRouter

app_name = "services"
router = DefaultRouter()



router.register("company",company_sevice.CompanyViewSet , basename="company")

urlpatterns = [
    path("", include(router.urls)),
]
