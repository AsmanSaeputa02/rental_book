from django.urls import path, include
from . import views
from services.services_set import company_sevice,book,user_services,auth_service
from rest_framework.routers import DefaultRouter

app_name = "services"
router = DefaultRouter()



router.register("company",company_sevice.CompanyViewSet , basename="company")
router.register("book",book.BookViewSet , basename="book")
router.register("user", user_services.UserViewSet, basename="user")
router.register("auth", auth_service.AuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
] 
 