from rest_framework import serializers

from log.models import Log


class RegisterProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = (
            'account_name',
            'datetime_create',
        )


class RegisterProfileCreateSerializer(serializers.Serializer):
    field_list = serializers.ListField(required=True)
