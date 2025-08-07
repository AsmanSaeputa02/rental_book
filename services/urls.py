from django.urls import path, include
from . import views
from services.services_set import company_sevice,book,user_services,auth_service,rental_service,dashbord_service
from rest_framework.routers import DefaultRouter
from django.urls import get_resolver
import pprint

app_name = "api"
router = DefaultRouter()


router.register("company",company_sevice.CompanyViewSet , basename="company")
router.register("book",book.BookViewSet , basename="book")
router.register("user", user_services.UserViewSet, basename="user")
router.register("auth", auth_service.AuthViewSet, basename="auth")
router.register("rental", rental_service.RentalViewSet, basename="rental")
router.register("Dashboard", dashbord_service.DashboardViewSet, basename="Dashboard")
for url in router.urls:
    print("📦 Router URL:", url)
urlpatterns = [
    path("", include(router.urls)),
] 
 