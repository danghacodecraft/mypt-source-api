from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.configs import app_settings
from app.myCore.helpers.auth_session_handler import getUserAuthSessionData
from app.myHttp.Entities.user_infos_handler import UserInfosHandler
from app.myHttp.models.user_infos import UserInfos
from app.myHttp.serializers.user_infos_serializer import UserInfosSerializer
from app.myHttp.validations.proactively_update_device_token_validate import UpdateDeviceTokenValidate
from ...myCore.helpers.response import response_data
from app.myHttp.Apis.mypt_profile_apis import MyPtProfileApis


# Create your views here.
@api_view(["POST"])
def getUserDeviceInfoByEmail(request):
    postData = request.data
    userEmail = postData.get("email", None)
    if userEmail is None:
        respondedData = {
            "statusCode": 5,
            "message": "Missing email",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)

    # check user
    userInfosHandlerObj = UserInfosHandler()
    userInfo = userInfosHandlerObj.getUserByEmail(userEmail)
    if userInfo is None:
        respondedData = {
            "statusCode": 6,
            "message": "User not found by email",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)

    user_info = {
        "userId": int(userInfo["user_id"]),
        "email": userInfo["email"].lower(),
        "fullName": userInfo["full_name"],
        "empCode": "",
        "jobTitle": "",
        "childDepart": "",
        "agency": "",
        "parentDepart": "",
        "branch": "",
        "deviceToken": userInfo["device_token"],
        "deviceId": userInfo["device_id"],
        "deviceName": userInfo["device_name"],
        "devicePlatform": userInfo["device_platform"]
    }

    # goi qua mypt-profile-api de lay thong tin employee cua email nay
    user_email = userInfo["email"].lower()
    profile_apis = MyPtProfileApis()
    empsInfoData = profile_apis.getEmployeesInfoByEmails([user_email])
    for emp_info in empsInfoData:
        if emp_info["email"] == user_email:
            user_info["fullName"] = emp_info["full_name"]
            user_info["empCode"] = emp_info["emp_code"]
            user_info["jobTitle"] = emp_info["job_title"]
            user_info["childDepart"] = emp_info["child_depart"]
            user_info["agency"] = emp_info["agency"]
            user_info["parentDepart"] = emp_info["parent_depart"]
            user_info["branch"] = emp_info["branch"]
            break

    respondedData = {
        "statusCode": 1,
        "message": "Success",
        "data": user_info
    }
    return Response(respondedData, status.HTTP_200_OK)


@api_view(["POST"])
def getUserDevicesInfoByEmails(request):
    postData = request.data
    userEmails = postData.get("emails", [])
    if len(userEmails) <= 0:
        respondedData = {
            "statusCode": 5,
            "message": "Missing emails",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)

    userInfoQs = UserInfos.objects.filter(email__in=userEmails)
    userInfo_ser = UserInfosSerializer(userInfoQs, many=True)
    usersArr = userInfo_ser.data

    if len(usersArr) <= 0:
        respondedData = {
            "statusCode": 6,
            "message": "Users not found by emails",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)

    usersList = []
    user_emails = []
    for userItem in usersArr:
        usersList.append({
            "userId": int(userItem["user_id"]),
            "email": userItem["email"],
            "fullName": userItem["full_name"],
            "empCode": "",
            "jobTitle": "",
            "childDepart": "",
            "agency": "",
            "parentDepart": "",
            "branch": "",
            "deviceToken": userItem["device_token"],
            "deviceId": userItem["device_id"],
            "deviceName": userItem["device_name"],
            "devicePlatform": userItem["device_platform"]
        })
        user_emails.append(userItem["email"])

    # goi qua mypt-profile-api de lay thong tin employee cua cac email nay
    if len(user_emails) > 0:
        print(user_emails)
        profile_apis = MyPtProfileApis()
        empsInfoData = profile_apis.getEmployeesInfoByEmails(user_emails)
        for user_item in usersList:
            userItemEmail = user_item["email"].lower()
            for emp_info in empsInfoData:
                if emp_info["email"] == userItemEmail:
                    user_item["fullName"] = emp_info["full_name"]
                    user_item["empCode"] = emp_info["emp_code"]
                    user_item["jobTitle"] = emp_info["job_title"]
                    user_item["childDepart"] = emp_info["child_depart"]
                    user_item["agency"] = emp_info["agency"]
                    user_item["parentDepart"] = emp_info["parent_depart"]
                    user_item["branch"] = emp_info["branch"]
                    break


    respondedData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "usersList": usersList
        }
    }
    return Response(respondedData, status.HTTP_200_OK)


@api_view(["POST"])
def getEmailsByDeviceTokens(request):
    postData = request.data
    deviceTokens = postData.get("deviceTokens", [])
    if len(deviceTokens) <= 0:
        respondedData = {
            "statusCode": 5,
            "message": "Missing device token(s)",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)

    userInfoQs = UserInfos.objects.filter(device_token__in=deviceTokens).order_by("-date_login")
    userInfo_ser = UserInfosSerializer(userInfoQs, many=True)
    usersArr = userInfo_ser.data

    if len(usersArr) <= 0:
        respondedData = {
            "statusCode": 6,
            "message": "Users not found by device tokens",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)

    usersList = []
    existedDeviceTokens = []
    for userItem in usersArr:
        if userItem["device_token"] not in existedDeviceTokens:
            usersList.append({
                "email": userItem["email"],
                "deviceToken": userItem["device_token"]
            })
            existedDeviceTokens.append(userItem["device_token"])

    respondedData = {
        "statusCode": 1,
        "message": "Success",
        "data": {
            "usersList": usersList
        }
    }
    return Response(respondedData, status.HTTP_200_OK)


# API nay chi de goi private. API nay de lay user info (cu the la UserId) tu email. Neu chua co user info, se tao user acc tu email roi tra ve userId moi duoc tao
@api_view(["POST"])
def getOrCreateUserAccByEmail(request):
    userEmail = request.data.get("email", None)
    if userEmail is None:
        respondedData = {
            "statusCode": 5,
            "message": "Missing email",
            "data": None
        }
        return Response(respondedData, status.HTTP_200_OK)
    userEmail = userEmail.lower()

    userInfosHandlerObj = UserInfosHandler()
    # check email nay co trong bang user_infos hay chua
    userInfo = userInfosHandlerObj.getUserByEmail(userEmail)
    if userInfo is None:
        # Neu chua co, bat dau tao user acc cho email nay trong bang user_infos
        cutPosition = userEmail.find("@")
        fullName = userEmail[:cutPosition]
        resCreateUser = userInfosHandlerObj.createUser(userEmail, {
            "fullName": fullName
        })
        if resCreateUser.get("resCreate") == "SUCCESS":
            respondedData = {
                "statusCode": 1,
                "message": "User acc has been created successfully!",
                "data": {
                    "userId": resCreateUser.get("userId")
                }
            }
            return Response(respondedData, status.HTTP_200_OK)
        else:
            respondedData = {
                "statusCode": 4,
                "message": "User acc created failed!",
                "data": None
            }
            return Response(respondedData, status.HTTP_200_OK)
    else:
        respondedData = {
            "statusCode": 1,
            "message": "The email had user acc already!",
            "data": {
                "userId": int(userInfo.get("user_id"))
            }
        }
        return Response(respondedData, status.HTTP_200_OK)


# API mobile chủ động gọi lên khi mở app để update device_token
@api_view(["POST"])
def proactivelyUpdateDeviceToken(request):
    try:
        user_info_in_redis = getUserAuthSessionData(request.headers.get("Authorization"))
        user_email = user_info_in_redis.get('email', None)
        data = request.data.copy()
        device_info_validate = UpdateDeviceTokenValidate(data=data)

        if not device_info_validate.is_valid():
            return Response({
                "status": 4,
                "data": device_info_validate.errors,
                "message": "input invalid"
            }, status.HTTP_200_OK)

        device_info_validate = device_info_validate.data
        user = UserInfos.objects.filter(email=user_email).first()

        if user:
            keys = device_info_validate.keys()
            for key in keys:
                setattr(user, key, device_info_validate[key])
            user.save()

        return Response({
            "status": 1,
            "data": {},
            "message": "success"
        }, status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({
            "status": 4,
            "data": {},
            "message": str(e)
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def get_user_id_by_email(request):
    body_data = request.data

    if "email" not in body_data:
        return response_data(statusCode=5, message="Missing email")

    if body_data["email"] is None or body_data["email"] == "":
        return response_data(statusCode=5, message="Invalid email")

    user_info_queryset = UserInfos.objects.filter(email=body_data["email"]).first()
    if user_info_queryset:
        data = {
            "userId": user_info_queryset.user_id
        }
        return response_data(data=data)
    else:
        return response_data(statusCode=6, message="User Id not found with this email")
