from rest_framework.response import Response
from rest_framework.views import APIView

from crawler.models import App
from crawler.serializers import AppSerializer


class AppList(APIView):
    def get(self, request, format=None):
        users = App.objects.all()[:25]
        serializer = AppSerializer(users, many=True)
        return Response(serializer.data)
