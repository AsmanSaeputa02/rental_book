import uuid
from tests.base import BaseTenantTestCase
from user.models import User
from book.models import Book
from rental.functions.rental import RentalService
from dashbord.functions.dashbord import DashboardService


class DashboardServiceTest(BaseTenantTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="u@x.com", password="pass")
        self.book1 = Book.objects.create(
            title="Book One",
            author="Auth1",
            isbn=uuid.uuid4().hex[:13]
        )
        self.book2 = Book.objects.create(
            title="Book Two",
            author="Auth2",
            isbn=uuid.uuid4().hex[:13]
        )

    def test_dashboard_counts(self):
        RentalService.rent_book(user_id=self.user.id, book_id=self.book1.id)
        RentalService.rent_book(user_id=self.user.id, book_id=self.book2.id)

        data = DashboardService.get_dashboard_data(limit=2)
        self.assertEqual(data["total_rentals"], 2)
        self.assertEqual(len(data["top_books"]), 2)
