from account.models import Account
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView

from tmb_test.TMB_test_git.tmb_api.account.response import Response


class AccountDetailSerializer(serializers.ModelSerializer):
    id_card = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'code',
            'email',
            'username',
            'title',
            'first_name',
            'middle_name',
            'last_name',
            'id_card',
            'phone',
            'date_joined',
            'is_active',
        )

    def get_id_card(self, account):
        return account.id_card_decrypt


class AccountView(RetrieveAPIView):
    queryset = Account.objects.order_by('-is_active', '-id').distinct()
    serializer_class = AccountDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
