from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from crawler.models import App, User
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
        user = request.user
        recommendation_user = User.objects.filter(email=user.email)
        if not recommendation_user:
            return Response(data={'status': 404}, status=status.HTTP_404_NOT_FOUND)

        queryset = App.objects.all()
        serializer = AppSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        recommendation_user = User.objects.filter(email=user.email)
        if not recommendation_user:
            recommendation_user = User()
            recommendation_user.name = user.username
            recommendation_user.email = user.email
            recommendation_user.save()

        serializer = PackageNameSerialize(data=request.data, many=True)
        if serializer.is_valid():
            valid_data = serializer.validated_data
            headers = self.get_success_headers(serializer.data)
            return Response(data=valid_data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(data={'status': 400}, status=status.HTTP_400_BAD_REQUEST)
