import json
import pytz
import datetime

from Crypto.Cipher import AES
from account.models import Account, MemberType
from account.response import Response
from account.encryption import SECRET_KEY
from django.contrib.auth import login
from django.core.validators import validate_email, ValidationError
from register_profile.register import Register
from rest_framework import serializers
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny

from .config_register import data as config_register
from account.models import Session

from .encryption import AESCipher


class AccountSerializer(serializers.ModelSerializer):
    id_card = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
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
                            'is_active',)

    def get_id_card(self, account):
        return account.id_card_decrypt


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)
    email = serializers.CharField(max_length=255, required=False)
    salary = serializers.CharField(max_length=255, required=True)
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    middle_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    id_card = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=64, required=True)


def register(request, data, is_web):
    config_register_value = config_register['value_text']
    all_field = config_register_value['field_list']

    database_standard_field = {
        'username', 'email', 'password', 'salary', 'confirm_password', 'title', 'first_name', 'middle_name',
        'last_name', 'phone', 'id_card'
    }
    param_extra_field = {}
    # Check Empty Field
    for field in all_field:
        if not field['is_optional']:
            if field['key'] not in data:
                return {'detail': '%s_is_required' % field['key']}, status.HTTP_428_PRECONDITION_REQUIRED

        value = data.get(field['key'])
        if field['key'] in data and value and field['key'] not in str(database_standard_field):
            param_extra_field[field['key']] = value

        min_length = field.get('min_length')
        max_length = field.get('max_length')
        if min_length and value and len(value) < int(min_length) and max_length is None:
            return {'detail': '%s_length_error' % field['key']}, status.HTTP_400_BAD_REQUEST
        if max_length and value and len(value) > int(max_length) and min_length is None:
            return {'detail': '%s_length_error' % field['key']}, status.HTTP_400_BAD_REQUEST
        if max_length and value and len(value) > int(max_length) or min_length and value and len(value) < int(
                min_length):
            return {'detail': '%s_length_error' % field['key']}, status.HTTP_400_BAD_REQUEST

    username = Account.objects.filter(username__iexact=data.get('username', '').strip()).first()
    if username:
        return {'detail': 'username_has_been_already_use'}, status.HTTP_409_CONFLICT
    if data.get('email'):
        email = Account.objects.filter(email__iexact=data.get('email', '').strip()).first()
        if email:
            return {'detail': 'email_has_been_already_use'}, status.HTTP_409_CONFLICT
        try:
            validate_email(data.get('email'))
        except ValidationError:
            return {'detail': 'error_email_format'}, status.HTTP_400_BAD_REQUEST

    if data.get('confirm_password'):
        if data.get('password') != data.get('confirm_password'):
            return {'detail': 'password_not_match'}, status.HTTP_400_BAD_REQUEST
    salary = int(data.get('salary', ''))
    _type = -1
    if salary < 15000:
        return {'detail': 'Too cheap'}, status.HTTP_400_BAD_REQUEST
    elif salary < 30000:
        _type = 1
    elif 30000 <= salary <= 50000:
        _type = 2
    elif salary > 50000:
        _type = 3
    else:
        _type = 9001

    try:
        param_extra_field = json.dumps(param_extra_field)
    except:
        pass

    count_experience_dict = data.get('count_experience')
    if count_experience_dict:
        count_experience_year = count_experience_dict.get('count_experience_year')
        count_experience_month = count_experience_dict.get('count_experience_month')
        if count_experience_year is None and count_experience_month is None:
            count_experience = -1
        elif count_experience_year is None:
            count_experience = count_experience_month
        elif count_experience_month is None:
            count_experience = (count_experience_year * 12)
        else:
            count_experience = (count_experience_year * 12) + count_experience_month
    else:
        count_experience = -1
    # code = 'datejoin+ 4 lastdigit of phone'
    phone = data.get('phone', '')
    tz = pytz.timezone('Asia/Bangkok')
    str_datetime_now = datetime.datetime.now(tz).strftime('%Y%m%d')
    code = str_datetime_now + phone[-4:] if phone else str_datetime_now+'0000'

    id_card = (data.get('id_card', ''))
    id_card = AESCipher('d2%mxvbshq_vs#5h&9e_39iml4i#(uo&%@jfifokf&@$f*0c8-').encrypt(id_card)

    _account = Account.objects.create(
        username=data.get('username', '').strip(),
        email=data.get('email', '').strip().lower() if data.get('email') else None,
        title=data.get('title', ''),
        first_name=data.get('first_name', ''),
        middle_name=data.get('middle_name', ''),
        salary=data.get('salary', ''),
        last_name=data.get('last_name', ''),
        phone=phone,
        id_card=id_card,
        code=code
    )

    MemberType.objects.create(
        account=_account,
        type=_type
    )

    _account.set_password(data.get('password'))
    _account.save()

    login(request, _account, backend='django.contrib.auth.backends.ModelBackend')
    session_key = request.session.session_key
    if session_key is None:
        request.session.save()
        session_key = request.session.session_key
    Session.push(request.user, session_key)
    request.session.set_expiry(86400 * 365)

    return AccountSerializer(_account).data, status.HTTP_201_CREATED


# @api_view(['POST', 'GET'])
class RegisterView(ListCreateAPIView):
    queryset = Account.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer_data = serializer.data
        custom_data = {k: request.data[k] for k in set(request.data) - set(serializer.data)}
        data = {**serializer_data, **custom_data}
        response_data, status_response = register(request, data, False)
        return Response(data=response_data, status=status_response)

    def list(self, request, *args, **kwargs):
        register_form = Register()
        return Response(register_form.get_register_form_client)
