from rest_framework import serializers

from crawler.models import App, UserApps


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'package_name', 'name', 'icon_url', 'category_key', 'category_name', 'developer_name')


class FullAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'package_name', 'name', 'description', 'icon_url', 'category_key', 'category_name',
                  'developer_name', 'version', 'content_rating', 'size')


class UserAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApps
        fields = ('package_name',)
