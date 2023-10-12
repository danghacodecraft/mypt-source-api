import json
from rest_framework.viewsets import ViewSet
from ...myCore.helpers.response import response_data
from ...myCore.helpers import auth_session_handler as authSessionHandler
import uuid
from ..models.user_senders import *
from ..models.sender_tokens import *
from ..serializers.user_senders_serializer import *
from ..serializers.sender_tokens_serializer import *
from ..apis.fpt_ai_chat_apis import *
from django.conf import settings as project_settings
from ...configs import app_settings
from datetime import datetime
from ...myCore.helpers import utils as utHelper
from ..models.user_infos import UserInfos
from ..serializers.user_infos_serializer import UserInfosSerializer
from ..entities.permission_handler import *
from ..apis.mypt_profile_apis import MyPtProfileApis

class UserInfoView(ViewSet):
    # API nay chi dung de goi private. API nay de lay thong tin user, profile cua user do, thong tin employee cua user do
    def postUserInfoAndProfileByUserId(self, request):
        postData = request.data
        userId = postData.get("userId", 0)
        try:
            userId = int(userId)
        except:
            userId = 0

        if userId <= 0:
            return response_data(None, 5, "Missing userId param!")

        usQs = UserInfos.objects.filter(user_id=userId)[0:1]
        if not usQs.exists():
            return response_data(None, 5, "Invalid user info!")

        userInfo_ser = UserInfosSerializer(usQs, many=True)
        usersArr = userInfo_ser.data
        if len(usersArr) <= 0:
            return response_data(None, 5, "No user info by the userId")
        userInfoItem = usersArr[0]

        user_id = int(userInfoItem["user_id"])

        # lay ra cac permission ma user nay duoc gan de set vao perCodes
        perHandler = PermissionHandler()
        persData = perHandler.getAllPermissionsByUser(user_id)
        permissionsData = persData.get("persData")
        userPerCodes = []
        for perCode, perData in permissionsData.items():
            userPerCodes.append(perCode)

        # chuan bi data tra ve
        userInfoAndProfileData = {
            "userId": user_id,
            "email": userInfoItem["email"],
            "userPerCodes": userPerCodes,
            "isTinPncEmp": 0,
            "empInfo": {
                "jobTitle": "",
                "empCode": "",
                "childDepart": "",
                "branch": "",
                "parentDepart": "",
                "agency": ""
            }
        }

        # goi API ben mypt-profile-api de lay them thong tin profile, employees
        profileApis = MyPtProfileApis()
        profileInfoData = profileApis.getProfileInfo(user_id, userInfoItem["email"], userInfoItem.get("full_name", ""), {})
        if profileInfoData is not None:
            userInfoAndProfileData["isTinPncEmp"] = int(profileInfoData.get("isTinPncEmployee"))
            userInfoAndProfileData["empInfo"]["jobTitle"] = str(profileInfoData.get("jobTitle", ""))
            userInfoAndProfileData["empInfo"]["empCode"] = str(profileInfoData.get("empCode", ""))
            userInfoAndProfileData["empInfo"]["childDepart"] = str(profileInfoData.get("childDepart", ""))
            userInfoAndProfileData["empInfo"]["branch"] = str(profileInfoData.get("branch", ""))
            userInfoAndProfileData["empInfo"]["parentDepart"] = str(profileInfoData.get("parentDepart", ""))
            userInfoAndProfileData["empInfo"]["agency"] = str(profileInfoData.get("agency", ""))

        return response_data(userInfoAndProfileData, 1, "Success")


