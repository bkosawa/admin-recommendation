from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from crawler.models import App, User, UserApps
from crawler.serializers import AppSerializer, UserAppsSerializer, FullAppSerializer
from crawler.tasks import recommend_to_user


class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    http_method_names = ['get', 'options']

    def get_serializer_class(self):
        if self.action == 'list':
            return AppSerializer
        if self.action == 'retrieve':
            return FullAppSerializer
        return AppSerializer


class RecommendedAppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    http_method_names = ['get', 'post', 'options']

    def list(self, request, *args, **kwargs):
        user = request.user
        recommendation_user = User.objects.filter(email=user.email).first()
        if not recommendation_user:
            return Response(data={'status': 404}, status=status.HTTP_404_NOT_FOUND)

        recommended_apps = recommendation_user.recommended_apps.all()
        if not recommended_apps:
            return Response(data={'status': 404}, status=status.HTTP_404_NOT_FOUND)

        queryset = recommended_apps
        serializer = AppSerializer(queryset, many=True)
        list_count = recommended_apps.count()
        return Response({
            "count": list_count,
            "next": None,
            "previous": None,
            "results": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        recommendation_user = User.objects.filter(email=user.email).first()
        if not recommendation_user:
            recommendation_user = User()
            recommendation_user.name = user.username
            recommendation_user.email = user.email
            recommendation_user.save()
        else:
            UserApps.objects.filter(user_id=recommendation_user.id).delete()

        serializer = UserAppsSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(user=recommendation_user)
            recommend_to_user.delay(recommendation_user.id)
            headers = self.get_success_headers(serializer.data)
            return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(data={'status': 400}, status=status.HTTP_400_BAD_REQUEST)
