from django.shortcuts import render
from account.models import Account
from django.db.models import Subquery, Q
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    url(r'^$', schema_view)
]


def index(request):
    account = Account.objects.filter(Q(username=request.user) | Q(email=request.user)).first()
    return render(
        request,
        'index.html',
        {
            'account': account
        }
    )
