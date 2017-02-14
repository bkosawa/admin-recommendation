from django.conf.urls import patterns, url

from crawler import views

urlpatterns = patterns('',
                       url(r'^apps', views.AppList.as_view()),
                       )
