from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crawler.models import App


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('id', 'package_name', 'name', 'icon_url', 'category_key', 'developer_name')


class PackageNameSerialize(serializers.Serializer):
    package_name = serializers.CharField(max_length=256)

    def create(self, validated_data):
        return App(**validated_data)

    def update(self, instance, validated_data):
        instance.package_name = validated_data.get('package_name', instance.package_name)
        return instance

    def validate(self, data):
        if not data['package_name']:
            raise ValidationError({'package_name': 'This field is required.'})
        return data
