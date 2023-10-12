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

# Chi de tam o service nay. Sau nay dem qua mypt-chatbot-api
class ChatbotView(ViewSet):
    def getChatBotSenderInfo(self, request):
        authUserSesData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        # return response_data({"authSes": authUserSesData})

        userId = int(authUserSesData["userId"])
        # Check userId nay co trong bang user_senders chua (check userId nay co senderId chua)
        senderId = ""
        senderQs = UserSenders.objects.filter(user_id=userId)[0:1]
        senderExist = senderQs.exists()
        if senderExist:
            sender_sr = UserSendersSerializer(senderQs, many=True)
            senderData = sender_sr.data
            print(senderData[0])
            senderId = str(senderData[0].get("sender_id"))
            print("[getChatBotSenderInfo] Da ton tai SenderID cua userId " + str(userId) + " : " + senderId)
        else:
            # Tao sender ID, tuc la tao 1 row user_senders
            # Generate sender id
            uuidStr = uuid.uuid4()
            senderId = "userv13_" + str(userId) + "_" + str(uuidStr)
            print("[getChatBotSenderInfo] Chua ton tai SenderID cua userId " + str(userId) + ". Gio tao ra senderId de save vao DB : " + senderId)
            # insert row vao DB
            newSender = UserSenders(sender_id=senderId, user_id=userId, email=authUserSesData["email"])
            newSender.save()

        # return response_data({"senderId": senderId, "senderExist": senderExist})

        # check co param resetSenderToken hay ko
        alwaysCreateSenderToken = False
        resetSenderToken = request.data.get("resetSenderToken", None)
        if resetSenderToken is not None and int(resetSenderToken) == 1:
            alwaysCreateSenderToken = True

        senderToken = ""
        if alwaysCreateSenderToken == True:
            # goi API ben FPT.AI de tao sender_token tu senderId
            print("[getChatBotSenderInfo] Day la case luon luon tao moi Sender Token cho senderId : " + senderId)
            fptAiChat = FptAIChatApis()
            senderToken = fptAiChat.createSenderToken(senderId)
            if senderToken == "":
                return response_data(None, 4, "Create sender token failed!")
            # Xoa het sender token cua senderId nay trong DB truoc khi luu senderToken moi (update is_deleted thanh 1)
            SenderTokens.objects.filter(sender_id=senderId, is_deleted=0).update(is_deleted=1,date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # Luu senderToken vao DB
            newSenderTokenModel = SenderTokens(sender_token=senderToken, sender_id=senderId, user_id=userId,is_deleted=0)
            newSenderTokenModel.save()
        else:
            # Check senderId nay co trong bang sender_tokens chua (Check senderId nay co senderToken chua)
            tokenQs = SenderTokens.objects.filter(sender_id=senderId, is_deleted=0).order_by("-date_created")[0:1]
            tokenExist = tokenQs.exists()
            if tokenExist:
                token_sr = SenderTokensSerializer(tokenQs, many=True)
                tokenData = token_sr.data
                senderToken = str(tokenData[0].get("sender_token"))
                print("[getChatBotSenderInfo] Da tim thay sender token cua senderId " + senderId + " : " + senderToken)
            else:
                # goi API ben FPT.AI de tao sender_token tu senderId
                print("[getChatBotSenderInfo] Khong tim thay sender token cho senderId " + senderId + "! Can goi API ben FPT.AI de tao!")
                fptAiChat = FptAIChatApis()
                senderToken = fptAiChat.createSenderToken(senderId)
                if senderToken == "":
                    return response_data(None, 4, "Create sender token failed!")
                # Xoa het sender token cua senderId nay trong DB truoc khi luu senderToken moi (update is_deleted thanh 1)
                SenderTokens.objects.filter(sender_id=senderId, is_deleted=0).update(is_deleted=1, date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                # Luu senderToken vao DB
                newSenderTokenModel = SenderTokens(sender_token=senderToken, sender_id=senderId, user_id=userId, is_deleted=0)
                newSenderTokenModel.save()

        botCode = "e630ffb8776302ae1fb7441d34809b00"
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "production":
            botCode = "a2ccd43cb229f5e11ccf7a665c533e1d"

        loginUserDic = {
            "userId": userId,
            "email": authUserSesData["email"],
            "isTinPncEmp": int(authUserSesData.get("isTinPncEmployee", 0)),
            "empJobTitle": authUserSesData.get("jobTitle", ""),
            "empCode": authUserSesData.get("empCode", ""),
            "childDepart": authUserSesData.get("childDepart", ""),
            "branch": authUserSesData.get("branch", ""),
            "perCodes": []
        }
        # tap hop cac permission dang duoc gan voi user nay
        userPerCodes = []
        userPers = authUserSesData.get("permissions", {})
        for perCode, perData in userPers.items():
            userPerCodes.append(perCode)
        loginUserDic["perCodes"] = userPerCodes

        # ma hoa loginUserDic
        encodedLoginUserStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(loginUserDic))

        isAlwaysCreateSenderToken = 0
        if alwaysCreateSenderToken == True:
            isAlwaysCreateSenderToken = 1

        is_senderExist = 0
        if senderExist == True:
            is_senderExist = 1

        chatPayloadDict = {
            "login_user_token": encodedLoginUserStr,
            "mypt_user_id": str(userId),
            "mypt_user_email": authUserSesData["email"],
            "empJobTitle": authUserSesData.get("jobTitle", ""),
            "empCode": authUserSesData.get("empCode", ""),
            "childDepart": authUserSesData.get("childDepart", ""),
            "workingBranch": authUserSesData.get("branch", "")
        }
        chatPayloadArr = []
        for chatVarName, chatVarVal in chatPayloadDict.items():
            chatPayloadArr.append({
                "variable": chatVarName,
                "value": chatVarVal
            })

        # TAM THOI dung 1 senderToken gia
        senderToken = "dIYz6omOCKMV-qVS-p4nSof4pzfUJYNdbehD-LGRxXVwvOvnawJiU57iHYhSxeMjPNdnQvzeioZHPIbSwyKMIyJxO8TEnS3DUwjuKmqNv7bjC3q8qS0Mp4l1RPyZWVu"

        return response_data({
            "alwaysCreateSenderToken": isAlwaysCreateSenderToken,
            "botCode": botCode,
            "senderId": senderId,
            "senderExist": is_senderExist,
            "senderToken": senderToken,
            "senderName": authUserSesData.get("fullName", ""),
            "chatPayloadVars": chatPayloadArr
        })


    def getChatBotSenderInfoNew(self, request):
        authUserSesData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        # return response_data({"authUserSes": authUserSesData})

        userId = int(authUserSesData["userId"])
        # Check userId nay co trong bang user_senders chua (check userId nay co senderId chua)
        senderId = ""
        senderQs = UserSenders.objects.filter(user_id=userId)[0:1]
        senderExist = senderQs.exists()
        if senderExist:
            sender_sr = UserSendersSerializer(senderQs, many=True)
            senderData = sender_sr.data
            print(senderData[0])
            senderId = str(senderData[0].get("sender_id"))
            print("[getChatBotSenderInfo] Da ton tai SenderID cua userId " + str(userId) + " : " + senderId)
        else:
            # Tao sender ID, tuc la tao 1 row user_senders
            # Generate sender id
            uuidStr = uuid.uuid4()
            senderId = "user_" + str(userId) + "_" + str(uuidStr)
            print("[getChatBotSenderInfo] Chua ton tai SenderID cua userId " + str(userId) + ". Gio tao ra senderId de save vao DB : " + senderId)
            # insert row vao DB
            newSender = UserSenders(sender_id=senderId, user_id=userId, email=authUserSesData["email"])
            newSender.save()

        # return response_data({"senderId": senderId, "senderExist": senderExist})

        # check co param resetSenderToken hay ko
        alwaysCreateSenderToken = False
        resetSenderToken = request.data.get("resetSenderToken", None)
        if resetSenderToken is not None and int(resetSenderToken) == 1:
            alwaysCreateSenderToken = True

        senderToken = ""
        if alwaysCreateSenderToken == True:
            # goi API ben FPT.AI de tao sender_token tu senderId
            print("[getChatBotSenderInfo] Day la case luon luon tao moi Sender Token cho senderId : " + senderId)
            fptAiChat = FptAIChatApis()
            senderToken = fptAiChat.createSenderToken(senderId)
            if senderToken == "":
                return response_data(None, 4, "Create sender token failed!")
            # Xoa het sender token cua senderId nay trong DB truoc khi luu senderToken moi (update is_deleted thanh 1)
            SenderTokens.objects.filter(sender_id=senderId, is_deleted=0).update(is_deleted=1,
                                                                                 date_modified=datetime.now().strftime(
                                                                                     "%Y-%m-%d %H:%M:%S"))
            # Luu senderToken vao DB
            newSenderTokenModel = SenderTokens(sender_token=senderToken, sender_id=senderId, user_id=userId,
                                               is_deleted=0)
            newSenderTokenModel.save()
        else:
            # Check senderId nay co trong bang sender_tokens chua (Check senderId nay co senderToken chua)
            tokenQs = SenderTokens.objects.filter(sender_id=senderId, is_deleted=0).order_by("-date_created")[0:1]
            tokenExist = tokenQs.exists()
            if tokenExist:
                token_sr = SenderTokensSerializer(tokenQs, many=True)
                tokenData = token_sr.data
                senderToken = str(tokenData[0].get("sender_token"))
                print("[getChatBotSenderInfo] Da tim thay sender token cua senderId " + senderId + " : " + senderToken)
            else:
                # goi API ben FPT.AI de tao sender_token tu senderId
                print("[getChatBotSenderInfo] Khong tim thay sender token cho senderId " + senderId + "! Can goi API ben FPT.AI de tao!")
                fptAiChat = FptAIChatApis()
                senderToken = fptAiChat.createSenderToken(senderId)
                if senderToken == "":
                    return response_data(None, 4, "Create sender token failed!")
                # Xoa het sender token cua senderId nay trong DB truoc khi luu senderToken moi (update is_deleted thanh 1)
                SenderTokens.objects.filter(sender_id=senderId, is_deleted=0).update(is_deleted=1, date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                # Luu senderToken vao DB
                newSenderTokenModel = SenderTokens(sender_token=senderToken, sender_id=senderId, user_id=userId, is_deleted=0)
                newSenderTokenModel.save()

        botCode = "78e2c21383e3b1f682e2b3868ca832d1"
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "production":
            botCode = "8fa5961b2ce6557b0159fdac2c0267cc"

        loginUserDic = {
            "userId": userId,
            "email": authUserSesData["email"],
            "isTinPncEmp": int(authUserSesData.get("isTinPncEmployee", 0)),
            "empJobTitle": authUserSesData.get("jobTitle", ""),
            "empCode": authUserSesData.get("empCode", ""),
            "childDepart": authUserSesData.get("childDepart", ""),
            "branch": authUserSesData.get("branch", ""),
            "perCodes": []
        }
        # tap hop cac permission dang duoc gan voi user nay
        userPerCodes = []
        userPers = authUserSesData.get("permissions", {})
        for perCode, perData in userPers.items():
            userPerCodes.append(perCode)
        loginUserDic["perCodes"] = userPerCodes

        # ma hoa loginUserDic
        encodedLoginUserStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(loginUserDic))

        isAlwaysCreateSenderToken = 0
        if alwaysCreateSenderToken == True:
            isAlwaysCreateSenderToken = 1

        is_senderExist = 0
        if senderExist == True:
            is_senderExist = 1

        chatbotPayloadVarsData = {
            "login_user_token": encodedLoginUserStr,
            "mypt_user_id": str(userId),
            "mypt_user_email": authUserSesData["email"],
            "empJobTitle": authUserSesData.get("jobTitle", ""),
            "empCode": authUserSesData.get("empCode", ""),
            "childDepart": authUserSesData.get("childDepart", ""),
            "workingBranch": authUserSesData.get("branch", "")
        }

        # TAM THOI dung 1 senderToken gia
        # senderToken = "dIYz6omOCKMV-qVS-p4nSof4pzfUJYNdbehD-LGRxXVwvOvnawJiU57iHYhSxeMjPNdnQvzeioZHPIbSwyKMIyJxO8TEnS3DUwjuKmqNv7bjC3q8qS0Mp4l1RPyZWVu"

        return response_data({
            "alwaysCreateSenderToken": isAlwaysCreateSenderToken,
            "botCode": botCode,
            "senderId": senderId,
            "senderExist": is_senderExist,
            "senderToken": senderToken,
            "senderName": authUserSesData.get("fullName", ""),
            "chatbotPayloadVars": chatbotPayloadVarsData
        })
