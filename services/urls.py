from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import ViewSets ทั้งหมด
from services.services_set import (
    company_sevice,
    book,
    user_services,
    auth_service,
    rental_service,
    dashbord_service,
    admin_login,
)

app_name = "api"
router = DefaultRouter()

# Register API endpoints
router.register("company", company_sevice.CompanyViewSet, basename="company")
router.register("book", book.BookViewSet, basename="book")
router.register("user", user_services.UserViewSet, basename="user")
router.register("auth", auth_service.AuthViewSet, basename="auth")
router.register("rental", rental_service.RentalViewSet, basename="rental")
router.register("dashboard", dashbord_service.DashboardViewSet, basename="dashboard")

# Debug print all router URLs
for url in router.urls:
    print("📦 Router URL:", url)

# Add manual path for admin login
urlpatterns = [
    path("", include(router.urls)),
    path("admin-login/", admin_login.AdminLoginView.as_view(), name="admin-login"),
]
