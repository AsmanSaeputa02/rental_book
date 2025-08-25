# services/services_set/rental_service.py 
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rental.functions.rental import RentalService  # เรียกใช้เฉพาะ service layer
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RentalViewSet(ViewSet):
    @swagger_auto_schema(
        operation_summary="ดูรายการเช่าทั้งหมด",
        operation_description="แสดงรายการการเช่าทั้งหมดในระบบของ tenant ปัจจุบัน",
        responses={
            200: openapi.Response(
                description="List of rentals",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "user_id": 2,
                            "book_id": 5,
                            "quantity": 2,
                            "rented_at": "2025-07-30T10:00:00Z",
                            "returned_at": None
                        }
                    ]
                }
            )
        }
    )
    def list(self, request):
        rentals = RentalService.get_all_rentals()
        return Response(rentals, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="เช่าหนังสือ (รองรับจำนวน)",
        operation_description="ผู้ใช้เช่าหนังสือตามจำนวนที่ต้องการ ระบบจะหักสต็อกจาก Book.available_count ตามจำนวนที่เช่า",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id", "book_id"],
            properties={
                "user_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID ของผู้ใช้งาน"
                ),
                "book_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID ของหนังสือ"
                ),
                "quantity": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="จำนวนเล่มที่ต้องการยืม (ค่าเริ่มต้น = 1)"
                ),
            },
            example={"user_id": 1, "book_id": 5, "quantity": 2}
        ),
        responses={
            201: openapi.Response(
                description="สร้างการเช่าหนังสือสำเร็จ",
                examples={
                    "application/json": {
                        "id": 12,
                        "user_id": 1,
                        "book_id": 5,
                        "quantity": 2,
                        "available_count": 7,  # คงเหลือหลังหักสต็อก
                        "rented_at": "2025-07-30T12:00:00Z"
                    }
                }
            ),
            400: openapi.Response(
                description="สต็อกไม่พอ หรือข้อมูลไม่ถูกต้อง",
                examples={"application/json": {"error": "Not enough books available"}}
            )
        }
    )
    def create(self, request):
        user_id = request.data.get("user_id")
        book_id = request.data.get("book_id")
        quantity = request.data.get("quantity", 1)

        # แปลงเป็น int แบบปลอดภัย
        try:
            user_id = int(user_id)
            book_id = int(book_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({"error": "user_id, book_id และ quantity ต้องเป็นจำนวนเต็ม"},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({"error": "quantity ต้องมากกว่า 0"}, status=status.HTTP_400_BAD_REQUEST)

        result = RentalService.rent_book(user_id, book_id, quantity)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="ดูรายการเช่ารายตัว",
        operation_description="ดูข้อมูลของ rental_id นั้น ๆ",
        responses={
            200: openapi.Response(description="Rental found"),
            404: openapi.Response(description="Rental not found")
        }
    )
    def retrieve(self, request, pk=None):
        result = RentalService.get_rental_by_id(pk)
        if not result:
            return Response({"error": "Rental not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="คืนหนังสือ",
        operation_description="คืนหนังสือที่เช่าไว้ โดยใช้ rental_id ใน URL ระบบจะบวกสต็อกคืนตาม quantity ที่เช่าไว้",
        responses={
            200: openapi.Response(
                description="คืนหนังสือสำเร็จ",
                examples={
                    "application/json": {
                        "status": "returned",
                        "returned_at": "2025-07-30T14:30:00Z",
                        "available_count": 9  # คงเหลือหลังบวกคืน
                    }
                }
            ),
            400: openapi.Response(
                description="ไม่พบ rental หรือคืนไปแล้ว",
                examples={"application/json": {"error": "Rental not found or already returned"}}
            )
        }
    )
    def update(self, request, pk=None):
        result = RentalService.return_book(pk)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="ลบการเช่า (และคืน stock ถ้ายังไม่ได้คืน)",
        operation_description="ลบรายการการเช่าออกจากระบบ",
        responses={
            204: openapi.Response(description="ลบสำเร็จ"),
            404: openapi.Response(description="ไม่พบ rental")
        }
    )
    def destroy(self, request, pk=None):
        result = RentalService.delete_rental(pk)
        if "error" in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @swagger_auto_schema(
    method='get',
    operation_summary="ประวัติการเช่าทั้งหมดที่เคยคืนแล้ว",
    responses={200: openapi.Response(description="Rental History")}
)
    @action(detail=False, methods=["get"], url_path="history")
    def rental_history(self, request):
        user_id = request.query_params.get("user_id")
        rentals = RentalService.get_rental_history(user_id)
        return Response(rentals, status=status.HTTP_200_OK)
