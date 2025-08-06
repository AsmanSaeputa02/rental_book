import uuid
from tests.base import BaseTenantTestCase
from user.models import User
from book.models import Book
from rental.functions.rental import RentalService

class RentalServiceTest(BaseTenantTestCase):
    def setUp(self):
        # สร้าง user
        self.user = User.objects.create_user(email="a@x.com", password="pass")

        # isbn ต้อง unique & <=13 chars => ใช้ uuid4.hex[:13]
        self.book1 = Book.objects.create(
            title="Test Book 1",
            author="Author1",
            isbn=uuid.uuid4().hex[:13]
        )
        self.book2 = Book.objects.create(
            title="Test Book 2",
            author="Author2",
            isbn=uuid.uuid4().hex[:13]
        )

    def test_rent_and_return_cycle(self):
        result = RentalService.rent_book(user_id=self.user.id, book_id=self.book1.id)
        self.assertIn("id", result)
        self.assertEqual(result["user_id"], self.user.id)

        returned = RentalService.return_book(result["id"])
        self.assertEqual(returned.get("status"), "returned")
