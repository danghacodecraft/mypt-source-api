from app.http.models.user_infos import UserInfos
from app.http.serializers.user_infos_serializer import UserInfosSerializer

class UserInfosHandler:
    def getAllUsers(self):
        userInfoQs = UserInfos.objects.all()
        userInfo_ser = UserInfosSerializer(userInfoQs, many=True)
        userInfosArr = userInfo_ser.data
        return userInfosArr

    def getUserByEmail(self, email):
        email = email.lower()
        # print("chuan bi tim user theo email : " + email)
        usQs = UserInfos.objects.filter(email=email)[0:1]
        userInfo_ser = UserInfosSerializer(usQs, many=True)
        usersArr = userInfo_ser.data
        # print(usersArr)
        if len(usersArr) > 0:
            userInfoItem = usersArr[0]
            print(userInfoItem)
            return userInfoItem
        else:
            return None

    def getUserByUserId(self, userId):
        print("chuan bi tim user theo User ID : " + str(userId))
        usQs = UserInfos.objects.filter(user_id=userId)[0:1]
        userInfo_ser = UserInfosSerializer(usQs, many=True)
        usersArr = userInfo_ser.data
        # print(usersArr)
        if len(usersArr) > 0:
            userInfoItem = usersArr[0]
            print(userInfoItem)
            return userInfoItem
        else:
            return None

    def createUser(self, email, userInfo):
        newUser = UserInfos()
        newUser.email = email.lower()
        newUser.full_name = userInfo.get("fullName")

        # xu ly cac thong tin device
        if userInfo.get("deviceId", None) is not None:
            newUser.device_id = userInfo.get("deviceId")
        if userInfo.get("deviceName", None) is not None:
            newUser.device_name = userInfo.get("deviceName")
        if userInfo.get("deviceToken", None) is not None:
            newUser.device_token = userInfo.get("deviceToken")
        if userInfo.get("devicePlatform", None) is not None:
            newUser.device_platform = userInfo.get("devicePlatform")

        newUser.app_language = userInfo.get("lang", "vi")
        newUser.app_version = userInfo.get("appVersion", "")

        if userInfo.get("dateLogin", None) is not None:
            newUser.date_login = userInfo.get("dateLogin")

        newUser.unread_notify = 1
        newUser.is_deleted = 0
        resInsert = newUser.save()
        print(resInsert)
        newUserId = newUser.user_id
        print("new user id : " + str(newUserId))

        if int(newUserId) > 0:
            return {"resCreate": "SUCCESS", "userId": int(newUserId)}
        else:
            return {"resCreate": "FAILED"}

    def updateUserInfoByUserId(self, userId, userInfo = {}):
        # cach 1 :
        updatedFields = []
        usQs = UserInfos.objects.get(user_id=userId)
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

        if userInfo.get("lang", None) is not None:
            usQs.app_language = userInfo.get("lang")
            updatedFields.append("app_language")

        if userInfo.get("appVersion", None) is not None:
            usQs.app_version = userInfo.get("appVersion")
            updatedFields.append("app_version")

        resUpdate = usQs.save(update_fields=updatedFields)

        return resUpdate

        # resUpdate = UserInfos.objects.filter(user_id=userId).update(device_id="newdeviceid", device_name="tuyen mobile", app_version="6.9.3")
        # print("Ket qua update userId " + str(userId) + " : " + str(resUpdate))
        # if resUpdate >= 1:
        #     return True
        # else:
        #     return False


    def updateUserInfoByEmail(self, email):
        return None