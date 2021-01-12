import logging

from django.contrib.auth import authenticate, login
from rest_framework import status

from .models import Account, Session
from .response import Response
from .serializers import AccountSerializer


def login_conicle(request, data, code, group='ACCOUNT_LOGIN'):
    logger = logging.getLogger('LOGIN')
    if data['password'] is None:
        return Response('Hacking!! password is None', status=status.HTTP_401_UNAUTHORIZED)

    account = authenticate(username=data['username'].strip().lower(), password=data['password'])
    if account is None:
        _account = Account.objects.filter(username__icontain=data['username'].strip().lower())
        return {'detail': 'error_email_pass_fail'}, status.HTTP_401_UNAUTHORIZED

    if not account.is_active:
        logger.info('406 Not Acceptable (%s) User is inactive' % data['username'])
        return {'detail': 'error_account_inactive'}, status.HTTP_406_NOT_ACCEPTABLE

    login(request, account)
    session_key = request.session.session_key
    if session_key is None:
        request.session.save()
        session_key = request.session.session_key
    Session.push(request.user, session_key)

    ip = get_client_ip(request)

    logger.info('200 OK (%s) Login Success' % data['username'])
    return AccountSerializer(account).data, status.HTTP_200_OK


def get_client_ip(request):
    if request is None:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
