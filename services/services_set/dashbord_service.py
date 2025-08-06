from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from dashbord.functions import dashbord

class DashboardViewSet(ViewSet):
    def list(self, request):
        data = dashbord.DashboardService.get_dashboard_data()
        return Response(data)
