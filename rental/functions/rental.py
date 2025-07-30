from rental.models import Rental
from book.models import Book
from user.models import User
from django.utils.timezone import now

class RentalService:
    @staticmethod
    def rent_book(user_id, book_id):
        if Rental.objects.filter(book_id=book_id, returned_at__isnull=True).exists():
            return {"error": "Book already rented"}

        rental = Rental.objects.create(user_id=user_id, book_id=book_id)
        return {
            "id": rental.id,
            "user_id": rental.user_id,
            "book_id": rental.book_id,
            "rented_at": rental.rented_at
        }

    @staticmethod
    def return_book(rental_id):
        try:
            rental = Rental.objects.get(id=rental_id, returned_at__isnull=True)
            rental.returned_at = now()
            rental.save()
            return {"status": "returned", "returned_at": rental.returned_at}
        except Rental.DoesNotExist:
            return {"error": "Rental not found or already returned"}

    @staticmethod
    def get_all_rentals():
        return list(Rental.objects.values("id", "user_id", "book_id", "rented_at", "returned_at"))
