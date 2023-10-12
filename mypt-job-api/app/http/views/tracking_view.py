from rest_framework.viewsets import ViewSet
from ...core.helpers.response import *
from ...core.helpers import auth_session_handler as authSessionHandler


class TrackingView(ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("====Safary===")

    def checkPassWord(self):
        return True

    def tracking_action(self, request):
        empCode = authSessionHandler.get_user_token(request).get("empCode", "")
        data = {
        }
        return response_data(data)
