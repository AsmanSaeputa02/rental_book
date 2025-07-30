from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rental.functions.rental import RentalService

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
                            "rented_at": "2025-07-30T10:00:00Z",
                            "returned_at": None
                        }
                    ]
                }
            )
        }
    )
    def list(self, request):
        return Response(RentalService.get_all_rentals())

    @swagger_auto_schema(
        operation_summary="เช่าหนังสือ",
        operation_description="ผู้ใช้เช่าหนังสือ 1 เล่ม หากเล่มนั้นยังไม่ถูกเช่าอยู่",
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
            },
            example={"user_id": 1, "book_id": 5}
        ),
        responses={
            201: openapi.Response(
                description="สร้างการเช่าหนังสือสำเร็จ",
                examples={
                    "application/json": {
                        "id": 12,
                        "user_id": 1,
                        "book_id": 5,
                        "rented_at": "2025-07-30T12:00:00Z"
                    }
                }
            ),
            400: openapi.Response(
                description="หนังสือถูกเช่าอยู่แล้ว หรือข้อมูลไม่ถูกต้อง",
                examples={"application/json": {"error": "Book already rented"}}
            )
        }
    )
    def create(self, request):
        user_id = request.data.get("user_id")
        book_id = request.data.get("book_id")
        result = RentalService.rent_book(user_id, book_id)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="คืนหนังสือ",
        operation_description="คืนหนังสือที่เช่าไว้ โดยใช้ rental_id ใน URL",
        responses={
            200: openapi.Response(
                description="คืนหนังสือสำเร็จ",
                examples={
                    "application/json": {
                        "status": "returned",
                        "returned_at": "2025-07-30T14:30:00Z"
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
        return Response(result)
