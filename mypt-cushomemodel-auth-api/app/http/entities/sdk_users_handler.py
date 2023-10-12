from ..models.sdk_users import SdkUsers
from ..serializers.sdk_users_serializer import SdkUsersSerializer

class SdkUsersHandler:

    # tim sdk_users theo app_id va acc_username
    def getUserByAccUsername(self, appId, accUsername):
        accUsername = accUsername.lower().strip()
        print("chuan bi tim user theo appId va accUsername : " + appId + " ; " + accUsername)
        usQs = SdkUsers.objects.filter(app_id=appId, acc_username=accUsername)[0:1]
        user_ser = SdkUsersSerializer(usQs, many=True)
        usersArr = user_ser.data
        if len(usersArr) > 0:
            userItem = usersArr[0]
            print(userItem)
            return userItem
        else:
            return None

    def getUserByUserId(self, userId):
        # print("chuan bi tim user theo User ID : " + str(userId))
        usQs = SdkUsers.objects.filter(user_id=userId)[0:1]
        userInfo_ser = SdkUsersSerializer(usQs, many=True)
        usersArr = userInfo_ser.data
        # print(usersArr)
        if len(usersArr) > 0:
            userInfoItem = usersArr[0]
            print(userInfoItem)
            return userInfoItem
        else:
            return None

    def createUser(self, appId, accUsername, userInfo = {}):
        newUser = SdkUsers()
        newUser.app_id = appId
        newUser.acc_username = accUsername.lower().strip()
        newUser.full_name = userInfo.get("fullName", "")

        # xu ly cac thong tin device
        if userInfo.get("deviceId", None) is not None:
            newUser.device_id = userInfo.get("deviceId")
        if userInfo.get("deviceName", None) is not None:
            newUser.device_name = userInfo.get("deviceName")
        if userInfo.get("deviceToken", None) is not None:
            newUser.device_token = userInfo.get("deviceToken")
        if userInfo.get("devicePlatform", None) is not None:
            newUser.device_platform = userInfo.get("devicePlatform")

        newUser.app_version = userInfo.get("appVersion", "")

        if userInfo.get("dateLogin", None) is not None:
            newUser.date_login = userInfo.get("dateLogin")

        newUser.is_deleted = 0
        resInsert = newUser.save()
        newUserId = newUser.user_id
        print("new SDK user id : " + str(newUserId))

        if int(newUserId) > 0:
            return {"resCreate": "SUCCESS", "sdkUserId": int(newUserId)}
        else:
            return {"resCreate": "FAILED"}

    def updateUserInfoByUserId(self, userId, userInfo = {}):
        updatedFields = []
        usQs = SdkUsers.objects.get(user_id=userId)
        if userInfo.get("fullName", None) is not None:
            usQs.full_name = userInfo.get("fullName")
            updatedFields.append("full_name")

        if userInfo.get("deviceId", None) is not None:
            usQs.device_id = userInfo.get("deviceId")
            updatedFields.append("device_id")

        if userInfo.get("deviceName", None) is not None:
            usQs.device_name = userInfo.get("deviceName")
            updatedFields.append("device_name")

        if userInfo.get("deviceToken", None) is not None:
            usQs.device_token = userInfo.get("deviceToken")
            updatedFields.append("device_token")

        if userInfo.get("devicePlatform", None) is not None:
            usQs.device_platform = userInfo.get("devicePlatform")
            updatedFields.append("device_platform")

        if userInfo.get("dateLogin", None) is not None:
            usQs.date_login = userInfo.get("dateLogin")
            updatedFields.append("date_login")

        if userInfo.get("dateLatestRefreshToken", None) is not None:
            usQs.date_latest_refresh_token = userInfo.get("dateLatestRefreshToken")
            updatedFields.append("date_latest_refresh_token")

        if userInfo.get("appVersion", None) is not None:
            usQs.app_version = userInfo.get("appVersion")
            updatedFields.append("app_version")

        resUpdate = usQs.save(update_fields=updatedFields)

        return resUpdate