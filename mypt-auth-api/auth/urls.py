from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from ..app.configs import app_settings as main_app_settings

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(main_app_settings.ROUTES_PREFIX, include("app.urls"))
]
