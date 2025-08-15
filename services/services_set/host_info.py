from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

class WhoAmIView(APIView):
    authentication_classes = []  # สาธารณะ
    permission_classes = []

    def get(self, request):
        return Response({
            "current_schema": getattr(connection, "schema_name", None),
            "host": request.get_host(),
            "path": request.path,
            "is_authenticated": request.user.is_authenticated,
            "user": getattr(request.user, "email", None),
        })
