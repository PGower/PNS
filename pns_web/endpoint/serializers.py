from endpoint.models import Mapping
from rest_framework import serializers


class MappingSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10, min_length=2)
    computer_name = serializers.CharField(max_length=50)
    ip_address = serializers.IPAddressField()
    created = serializers.DateTimeField(read_only=True)
    expired = serializers.BooleanField(read_only=True)
    fullname = serializers.CharField(write_only=True)
    action = serializers.ChoiceField(["login", "logout", "update"])

    def create(self, validated_data):
        filtered_data = {
            'username': validated_data.get('username'),
            'computer_name': validated_data.get('computer_name'),
            'ip_address': validated_data.get('ip_address'),
            'action': validated_data.get('action')
        }
        m = Mapping(**filtered_data)
        m.save()
        return m

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.computer_name = validated_data.get('computer_name', instance.computer_name)
        instance.ip_address = validated_data.get('ip_address', instance.ip_address)
        instance.save()
        return instance


class FullnameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10, min_length=2)
    fullname = serializers.CharField(max_length=255)

