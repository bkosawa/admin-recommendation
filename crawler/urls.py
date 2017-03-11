from django.conf.urls import patterns, url, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from crawler import views

router = routers.DefaultRouter()
router.register(r'apps', views.AppViewSet)
router.register(r'recommended-apps', views.RecommendedAppViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       url(r'^api-token-auth/', obtain_auth_token)
                       )
