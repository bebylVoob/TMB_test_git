from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('account/', include('account.urls')),
    path('admin/', admin.site.urls),
]