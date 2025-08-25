# rental/functions/rental.py

from django.db import transaction
from rental.models import Rental , HistoryRental
from book.models import Book
from user.models import User
from django.utils.timezone import now

class RentalService:
    @staticmethod
    def rent_book(user_id, book_id , quantity=1):
        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(id=user_id)
                book = Book.objects.select_for_update().get(id=book_id)

                if book.available_count < quantity:
                    return {"error": "Not enough copies available"}

                book.available_count -= quantity
                book.save()

                rental = Rental.objects.create(user_id=user_id, book_id=book_id, quantity=quantity)
                return {
                    "id": rental.id,
                    "user_id": rental.user_id,
                    "book_id": rental.book_id,
                    "available_count": rental.quantity,
                    "rented_at": rental.rented_at
                }
        except User.DoesNotExist:
            return {"error": "User not found"}

    @staticmethod
    def return_book(rental_id):
        try:
            with transaction.atomic():
                rental = Rental.objects.select_for_update().get(id=rental_id, returned_at__isnull=True)

                book = rental.book
                book.available_count += rental.quantity
                book.save() 

                rental.returned_at = now()
                rental.save()

                HistoryRental.objects.create(
                book=rental.book,
                user=rental.user,
                quantity=rental.quantity,
                rented_at=rental.rented_at,
                returned_at=rental.returned_at
            )

            # ✅ ลบ Rental เดิมออกจากตะกร้า
            rental.delete()

            return {
                "status": "returned",
                "returned_at": rental.returned_at,
                "available_count": book.available_count
            }
        except Rental.DoesNotExist:
            return {"error": "Rental not found or already returned"}
        

    @staticmethod
    def get_rental_by_id(rental_id):
        try:
            rental = Rental.objects.get(id=rental_id ,returned_at__isnull=True )
            return {
                "id": rental.id,
                "user_id": rental.user_id,
                "book_id": rental.book_id,
                "quantity": rental.quantity,
                "rented_at": rental.rented_at,
                "returned_at": rental.returned_at
            }
        except Rental.DoesNotExist:
            return None

    @staticmethod
    def delete_rental(rental_id):
        try:
            rental = Rental.objects.get(id=rental_id)

            # ถ้ายังไม่คืน ให้บวก stock คืนก่อน
            if rental.returned_at is None:
                book = rental.book
                book.available_count += rental.quantity
                book.save()

            rental.delete()
            return {"status": "deleted"}
        except Rental.DoesNotExist:
            return {"error": "Rental not found"}

    @staticmethod
    def get_all_rentals():
        return list(
            Rental.objects.filter(returned_at__isnull=True)
            .values("id", 
                    "user_id",
                    "book_id", 
                    "quantity", 
                    "rented_at", 
                    "returned_at"
            )
        )
    @staticmethod
    def get_rental_history(user_id=None):
        queryset = HistoryRental.objects.filter(returned_at__isnull=False)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return list(
            queryset.values(
                "id", "user_id", "book_id", "quantity", "rented_at", "returned_at"
            ).order_by("-returned_at")
        )
