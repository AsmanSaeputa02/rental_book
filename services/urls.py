from django.urls import path, include
from rest_framework.routers import DefaultRouter

from services.services_set.company_sevice import CompanyViewSet
from services.services_set.book import BookViewSet
from services.services_set.user_services import UserViewSet
from services.services_set.auth_service import AuthViewSet
from services.services_set.rental_service import RentalViewSet
from services.services_set.dashbord_service import DashboardViewSet
from services.services_set.admin_login import AdminLoginView  # ถ้ามี


router = DefaultRouter()
router.register("company", CompanyViewSet, basename="company")
router.register("book", BookViewSet, basename="book")
router.register("user", UserViewSet, basename="user")
router.register("auth", AuthViewSet, basename="auth")
router.register("rental", RentalViewSet, basename="rental")
router.register("dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = [
    path("api/", include(router.urls)),   # => /book_project/api/<endpoint>/
]