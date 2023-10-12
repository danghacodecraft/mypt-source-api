"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from app.configs import app_settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(app_settings.ROUTES_PREFIX, include("app.urls"))
]

api_url_v1_patterns = [
    path(app_settings.ROUTES_PREFIX, include("app.urls"))

]

urlpatterns += [
    path(app_settings.ROUTES_PREFIX + 'schema/', SpectacularAPIView.as_view(urlconf=api_url_v1_patterns, api_version='v1'), name="schema_v1"),
    path(app_settings.ROUTES_PREFIX + "docs/", SpectacularSwaggerView.as_view(url_name="schema_v1"), name='swagger_v1'),
    path(app_settings.ROUTES_PREFIX + "redoc/", SpectacularRedocView.as_view(url_name="schema_v1"), name='redoc_v1')
]