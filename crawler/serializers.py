from rest_framework import serializers

from crawler.models import App


class AppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = App
        fields = ('package_name', 'name')
