from django.http import HttpResponse
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError

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


def log_in(request):
    print(request)
    return HttpResponse("Hello, world. You're at the polls index.")

# class HomeView(LoginView):
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(LoginView, self).dispatch(*args, **kwargs)

# register
    # Login
# get information


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
