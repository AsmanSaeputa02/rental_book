# tests/test_rental_api.py

import uuid
from django.conf import settings
from tests.base import BaseTenantTestCase
from user.models import User
from book.models import Book
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class RentalAPITest(BaseTenantTestCase):
    def setUp(self):
        super().setUp()

        # สร้าง user + token
        self.user = User.objects.create_user(email="b@x.com", password="pass")
        refresh = RefreshToken.for_user(self.user)

        # สร้าง Test Client และบังคับ Host header ให้เป็น tenant domain
        self.client = APIClient(HTTP_HOST="testschema.localhost")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # สร้างหนังสือ พร้อม isbn unique <=13 chars
        self.book = Book.objects.create(
            title="API Book",
            author="AuthorAPI",
            isbn=uuid.uuid4().hex[:13]
        )

        # เตรียม URL สำหรับ rental endpoints
        raw_prefix = getattr(settings, "WEB_REAL_PATH", "")
        if raw_prefix and not raw_prefix.startswith("/"):
            raw_prefix = f"/{raw_prefix}"
        self.base_url = f"{raw_prefix}/services/rental"

    def test_rental_endpoints(self):
        # 1) GET /services/rental/
        response = self.client.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # 2) POST /services/rental/
        response = self.client.post(f"{self.base_url}/", {
            "user_id": self.user.id,
            "book_id": self.book.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

        # 3) PUT /services/rental/{id}/
        rental_id = response.json()["id"]
        response = self.client.put(f"{self.base_url}/{rental_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "returned")
