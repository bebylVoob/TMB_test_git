from account.models import Account
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView, ListAPIView

from account.response import Response


class AccountDetailSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'code',
            'username',
            'title',
            'first_name',
            'middle_name',
            'last_name',
            'date_joined',
            'is_active',
            'type',
        )

    def get_type(self, instance):
        from account.models import MemberType
        mt = MemberType.objects.filter(account_id=instance.id).first()
        print(mt)
        return mt.get_type_display()


class AccountView(ListAPIView):
    queryset = Account.objects.order_by('-is_active', '-id').distinct()
    serializer_class = AccountDetailSerializer

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        instance = Account.objects.get(id=user_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
