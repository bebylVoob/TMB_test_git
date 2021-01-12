from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    id_card = serializers.SerializerMethodField()
    is_verified_email = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'title',
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'date_joined',
            'code',
            'id_card',
            'is_active'
        )
        read_only_fields = ('date_joined',
                            'is_active')
