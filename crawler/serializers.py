from rest_framework import serializers

from crawler.models import App, UserApps


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'package_name', 'name', 'icon_url', 'category_key', 'developer_name')


class UserAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApps
        fields = ('package_name',)
