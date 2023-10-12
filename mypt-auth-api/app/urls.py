from django.urls import path
from .http.views import token_view
from .http.views import login_view
from .http.views import user_view
from .http.views import permission_view
from .http.views.external_login import ExternalLoginViewSet
from .http.views.chatbot_view import ChatbotView
from .http.views.user_info_view import UserInfoView

urlpatterns = [
    # path('import-to-lsqs', login_view.importToLSQS),
    path('user-token', token_view.genUserToken),
    path('show-login', login_view.showLogin),
    path('login', login_view.showAzureLogin),
    path('adfs-token', login_view.getAdfsToken),
    path('azure-token', login_view.getAzureToken),
    path('do-auth', login_view.doAuth),
    path('logout', login_view.doLogout),
    path('health', login_view.healthCheck),
    path('gen-logginned-user-token', login_view.genLogginedUserToken),
    path('test-sleep', login_view.testSleep),
    path('test-get-user-session', login_view.testGetUserSession),
    path('test-no-auth', login_view.testNoAuth),
    path('get-user-device-info-by-email', user_view.getUserDeviceInfoByEmail),
    path('save-permission-route-to-redis', permission_view.savePermissionWithRouteToRedis),
    path('get-permission-route-from-redis', permission_view.getPermissionWithRouteFromRedis),
    path('get-user-devices-info-by-emails', user_view.getUserDevicesInfoByEmails),
    path('get-emails-by-device-tokens', user_view.getEmailsByDeviceTokens),
    path('get-create-user-acc-by-email', user_view.getOrCreateUserAccByEmail),
    path('proactively-update-device-token', user_view.proactivelyUpdateDeviceToken),
    path('get-user-id-by-email', user_view.get_user_id_by_email),
    path('get-chatbot-sender-info', ChatbotView.as_view({"post": "getChatBotSenderInfo"})),
    path('get-chatbot-sender-info-new', ChatbotView.as_view({"post": "getChatBotSenderInfoNew"})),
    path('user-info-and-profile-by-user-id', UserInfoView.as_view({"post": "postUserInfoAndProfileByUserId"})),
    
    path("sign-up-by-email", ExternalLoginViewSet.as_view({"post": "sign_up_by_email"})),
    path("verify-otp", ExternalLoginViewSet.as_view({"post": "verify_otp"})),
    path("resend-otp", ExternalLoginViewSet.as_view({"post": "resend_otp"})),
]
