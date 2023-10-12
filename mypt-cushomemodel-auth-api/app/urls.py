from django.urls import path

from .http.views.rsa_key_view import CusHomeModelRSAView
from .http.views.auth_views import CusHomeModelAuthView
from .http.views.health_view import HealthView

urlpatterns = [
    path('health', HealthView.as_view({'get': 'health'})),

    # Nhung API cho SDK goi
    path("validate-app-user-token", CusHomeModelAuthView.as_view({'post': 'validate_app_user_token'})),
    path("auth-user-token", CusHomeModelAuthView.as_view({'post': 'auth_user_token'})),

    # Nhung API dung de goi private
    path("gen-app-user-token", CusHomeModelAuthView.as_view({'post': 'gen_app_user_token'})),
    path("decrypt-rsa-token", CusHomeModelAuthView.as_view({'post': 'decrypt_rsa_token'})),
    path("decrypt-aes-token", CusHomeModelAuthView.as_view({'post': 'decrypt_aes_token'})),
    path('test-get-user-session', CusHomeModelAuthView.as_view({'post': 'test_get_user_session'})),
    path('cache-apps-rsa-keys', CusHomeModelRSAView.as_view({'post': 'cache_apps_rsa_keys'})),

    # những api chỉ được chạy trên local, nếu muốn chạy những api này thì phải đóng comment lại appusermiddleware
    path('cushomemodel-rsa', CusHomeModelRSAView.as_view({'get': 'list', 'post': 'create'})),
    path('cushomemodel-rsa-detail', CusHomeModelRSAView.as_view({'get': 'retrieve', 'delete': 'destroy'})),
    path('gen-app-token', CusHomeModelAuthView.as_view({'post': 'gen_app_key_token'})),
]
