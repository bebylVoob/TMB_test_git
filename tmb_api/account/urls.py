from django.urls import path

from . import views
from .views_login import Login, LoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', Login)
]