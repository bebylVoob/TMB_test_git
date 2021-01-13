from django.urls import path
from rest_framework import routers

from . import views
from .views_login import LoginView
from .views_register import RegisterView
from .views_user import AccountView

router = routers.DefaultRouter()

urlpatterns = [
    path('', views.index, name='index'),
    path('log-in/', LoginView),
    path('register/', RegisterView.as_view(), name='register'),
    path('user-info/', AccountView.as_view(), name='Account info')
]
