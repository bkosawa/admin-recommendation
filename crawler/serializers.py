from rest_framework import serializers

from crawler.models import App


class AppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'package_name', 'name', 'icon_url', 'category_key', 'developer_name')
