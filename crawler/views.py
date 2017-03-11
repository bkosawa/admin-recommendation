from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from crawler.models import App
from crawler.serializers import AppSerializer, PackageNameSerialize


class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    http_method_names = ['get', 'options']


class RecommendedAppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    http_method_names = ['get', 'post', 'options']

    def list(self, request, *args, **kwargs):
        # To be used to identify recommendation
        user = request.user
        print user
        queryset = App.objects.all()
        serializer = AppSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # To be used to identify recommendation
        user = request.user
        print user
        serializer = PackageNameSerialize(data=request.data, many=True)
        if serializer.is_valid():
            valid_data = serializer.validated_data
            headers = self.get_success_headers(serializer.data)
            return Response(data=valid_data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(data={'status': 400}, status=status.HTTP_400_BAD_REQUEST)
