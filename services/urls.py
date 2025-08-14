# services/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from services.services_set.company_sevice import CompanyViewSet
from services.services_set.book import BookViewSet
from services.services_set.user_services import UserViewSet
from services.services_set.auth_service import AuthViewSet
from services.services_set.rental_service import RentalViewSet
from services.services_set.dashbord_service import DashboardViewSet

# APIView (ห้าม register กับ router)
from services.services_set.book_admin import AdminBookCreateView
from services.services_set.admin_login import AdminLoginView

app_name = "services"

router = DefaultRouter()
router.register(r"company",   CompanyViewSet,   basename="company")
router.register(r"book",      BookViewSet,      basename="book")
router.register(r"user",      UserViewSet,      basename="user")
router.register(r"auth",      AuthViewSet,      basename="auth")
router.register(r"rental",    RentalViewSet,    basename="rental")
router.register(r"dashboard", DashboardViewSet, basename="dashboard")


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/admin/book/create-in-tenant/", AdminBookCreateView.as_view(), name="admin-book-create-in-tenant"),
    path("api/admin/login/", AdminLoginView.as_view(), name="admin-login"),
]
