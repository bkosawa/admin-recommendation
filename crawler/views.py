from rest_framework import viewsets

from crawler.models import App
from crawler.serializers import AppSerializer


class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    http_method_names = ['get', 'options']
