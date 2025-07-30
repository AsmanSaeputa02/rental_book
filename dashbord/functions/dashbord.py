from django.db.models import Count
from rental.models import Rental

class DashboardService:
    @staticmethod
    def get_dashboard_data(limit=5):
        # ยอดการเช่าทั้งหมด
        total_rentals = Rental.objects.count()

        # หนังสือยอดนิยม 5 อันดับ (ตามจำนวน Rental)
        top_qs = (
            Rental.objects
            .values('book__title')
            .annotate(count=Count('id'))
            .order_by('-count')[:limit]
        )
        top_books = [
            {"title": item['book__title'], "count": item['count']}
            for item in top_qs
        ]

        return {
            "total_rentals": total_rentals,
            "top_books": top_books
        }
