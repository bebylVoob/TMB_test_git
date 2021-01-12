import ast
import uuid

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import ValidationError, NotFound

from .models import Account
from .response import Response
from .views_login_conicle import login_conicle


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=4)

    def validate_password(self, value):
        if len(value) < 4:
            raise ValidationError('Language not in Config')
        else:
            return value


class HomeView(LoginView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)


class LoginView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    allow_redirects = True
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data, status_response = login_conicle(request, data, 'WEB_CONICLE')
        return Response(data=data, status=status_response)
