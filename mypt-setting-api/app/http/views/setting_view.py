from app.core.helpers.auth_session_handler import getUserAuthSessionData
from app.http.models.setting_users_home_tabs_model import SettingUserHomeTabs
from ..models.setting_config_model import *
from ..serializers.setting_config_serializer import *

from ..models.ptq import *
from ..models.setting_home_tabs_model import *
from ..models.setting_function_icons_model import *
from ..serializers.ptq_serializer import *
from ..serializers.setting_home_tabs_serializer import *
from ..serializers.setting_users_home_tabs_serializer import SettingUsersHomeTabsSerializer
from core.helpers.response import *
from rest_framework.viewsets import ViewSet
import json
# from datetime import datetime
from datetime import timedelta
from django.conf import settings as project_settings
from ...configs.service_api_config import SERVICE_CONFIG
from django.db import IntegrityError, transaction
from django.db import connection
from ..apis.mypt_auth_apis import MyPtAuthApis
from ..models.setting_function_icons_model import SettingFunctionIcons
from ..serializers.setting_function_icons_serializer import SettingFunctionIconsSerializer
from ..threading.handle_company import *
from app.core.helpers.utils import *
import redis
import ast
from core.helpers.birthday_is_today import birthday_is_today
from django.db.models import Q
from ..models.theme_model import ThemeManager
from ..serializers.theme_manager_serializer import ThemeManagerSerializer
from core.helpers.configs import get_config, remove_config


# Just only has 1 CRUD API
class SettingView(ViewSet):

    def postConfigs(self, request):
        try:
            data_token = getUserAuthSessionData(request.headers.get("Authorization"))
            email = data_token.get("email", "")
            userId = data_token.get("userId", 0)
            user_device_id = data_token.get("deviceId", "")

            # Ptq
            self.getShowPtq(email=email, userId=userId)
            
            forceUpdateData = None
            postData = request.data

            curAppVerStr = postData.get("curAppVer", None)
            if curAppVerStr is None:
                return response_data(None, 5, "Missing app ver")
            curAppVerStr = str(curAppVerStr).strip()
            if curAppVerStr == "":
                return response_data(None, 5, "App ver is empty")
            curAppVerParts = curAppVerStr.split(".")
            curAppVerPartsCount = len(curAppVerParts)
            if curAppVerPartsCount <= 1 or curAppVerPartsCount > 3:
                return response_data(None, 5, "App ver is invalid")
            curAppVerPartsIsValid = True
            
            for verPart in curAppVerParts:
                verPart = str(verPart).strip()
                try:
                    verPart = int(verPart)
                except Exception as ex:
                    verPart = -1
                if verPart < 0:
                    curAppVerPartsIsValid = False
                    break

            if curAppVerPartsIsValid == False:
                return response_data(None, 5, "App ver parts is invalid")
            
            fullCurAppVerStr = ""
            if curAppVerPartsCount == 2:
                fullCurAppVerStr = curAppVerStr + ".0"
            else:
                fullCurAppVerStr = curAppVerStr

            queryset = SettingConfig.objects.filter(config_key="LATEST_APP_VERSION_INFO")[0:1]
            serializer = SettingConfigSerializer(queryset, many=True)
            configsArr = serializer.data
            if len(configsArr) > 0:
                forceUpdateData = self.validateAppVersion(configsArr[0], curAppVerStr)

            session_data = getUserAuthSessionData(request.headers.get("Authorization"))
            logginedUserId = session_data.get("userId")
            shownTabsList = self.getShownTabsByUserId(logginedUserId, fullCurAppVerStr)

            user_info = session_data
            user_permissions = user_info['permissions'].keys()

            user_birthday = data_token.get("birthday", None)
            user_sex = data_token.get("sex", None)
            theme_query = None
            today = datetime.now()
            birthday_is_today_verifier = birthday_is_today(user_birthday)
            
            if birthday_is_today_verifier:
                if user_sex == "F":
                    theme_query = Q(theme_code="birthday_female")
                else:
                    theme_query = Q(theme_code="birthday_male")

            else:
                theme_query = Q(start_date__lte=today, due_date__gte=today)

            themes_queryset = ThemeManager.objects.filter(theme_query)
            if not birthday_is_today_verifier:
                has_all_theme = themes_queryset.filter(branch="ALL")
                if has_all_theme:
                    theme_queryset = has_all_theme.first()
                else:
                    theme_queryset = themes_queryset.filter(branch=user_info.get("branch", "ALL") or "ALL").first()
            theme_data = ThemeManagerSerializer(theme_queryset).data if theme_queryset else {}

            # if theme_data:
            #     function_icons_query = Q(theme_id=theme_data['id'])
            # else:
            #     function_icons_query = Q(theme_id=None)

            # settingFunctionIconsQueryset = SettingFunctionIcons.objects.filter(function_icons_query).order_by("ordering")

            # if not settingFunctionIconsQueryset:

            settingFunctionIconsQueryset = SettingFunctionIcons.objects.filter(
                Q(
                    theme_id=None, 
                    on_home=True
                )
            ).order_by("ordering")

            settingFunctionIconsSerializer = SettingFunctionIconsSerializer(settingFunctionIconsQueryset, many=True)
            data_group_type = settingFunctionIconsQueryset.filter(group_type__isnull=False).values_list('group_type', flat=True)

            functionIconsList = settingFunctionIconsSerializer.data
            functionMessages = get_config("FUNCTION_STATUS_MESSAGES")

            for functionIcon in functionIconsList:
                functionIcon['imageUrl'] = functionIcon['setIcon'].get("sectionIcon", None)
                functionIconPermission = functionIcon['permissionCodes'].split(",")

                if "WORKING" != functionIcon['featureStatus']:
                    functionIcon["featureMessage"] = functionMessages[functionIcon["featureStatus"]]
                    functionIcon['featureStatus'] = False
    
                elif not(
                    "ALL" 
                    in user_permissions
                    or bool(list(
                        set(functionIconPermission) 
                        & set(user_permissions)
                    ))
                    or functionIconPermission == ['']
                ):
                    functionIcon["featureMessage"] = functionMessages["NO_PERMISSION"]
                    functionIcon['featureStatus'] = False
                else:
                    functionIcon["featureMessage"] = ""
                    functionIcon['featureStatus'] = True
                    
            appEnv = str(project_settings.APP_ENVIRONMENT)

            improvedCarWebKitUrl = get_config("IMPROVED_CAR_URL")[appEnv]
            chatBotUrl = get_config("CHATBOT_URL")[appEnv]
            miniGameData = get_config("MINIGAME_DATA")[appEnv]
            homeNewsUrl = get_config("HOME_NEWS_URL")[appEnv]
            newsAllUrl = get_config("NEWS_ALL_URL")[appEnv]
            houseSDKUrl = get_config("HOUSE_SDK_URL")[appEnv]
            surveyUrl = get_config("LABOR_SAFETY_SURVEY_URL")[appEnv] if (
                get_config("SURVEY_ACTIVATE_FLAG").get("value", False) 
                and self._check_survey(request.headers.get("Authorization"))
            ) else None

            data = {
                "deviceIdRegister": user_device_id,
                "screenType": data_token.get("screenType", 0),
                "listGroup": list(set(data_group_type)),
                "homeTabsList": shownTabsList,
                "functionIconsList": functionIconsList,
                "forceUpdateData": forceUpdateData,
                "lang": "vi",
                "homeNewsUrl": homeNewsUrl,
                "newsAllUrl": newsAllUrl,
                "improvedCarWebKitUrl": improvedCarWebKitUrl,
                "appEnv": appEnv,
                "logginedUserId": logginedUserId,
                "chatBotUrl": chatBotUrl,
                "theme": theme_data.get("theme_code", "default") or "default",
                "themeBackground": theme_data.get("theme_background", None) or get_config("DEFAULT_BACKGROUND")['url'],
                "appIcon": theme_data.get("icon_app", "default") or "default",
                "miniGameData": miniGameData,
                "houseSDKUrl": houseSDKUrl,
                "surveyUrl": surveyUrl
            }

            return response_data(data)
        except Exception as e:
            print(e)
            return response_data(str(e), statusCode=4)

    def getShowPtq(self, email, userId):
        if email != '':
            try:
                ptq = call_api(
                    host=SERVICE_CONFIG['COMPANY'][project_settings.APP_ENVIRONMENT],
                    func=SERVICE_CONFIG['COMPANY']['get_ptq_from_email']['func'],
                    method=SERVICE_CONFIG['COMPANY']['get_ptq_from_email']['method'],
                    data={"email": email},
                )
                if ptq:
                    ptq = json.loads(ptq)
                    ptq = ptq['data']
            except:
                ptq = []
            try:
                ptqTypesFromRedis = call_api(
                    host=SERVICE_CONFIG['COMPANY'][project_settings.APP_ENVIRONMENT],
                    func=SERVICE_CONFIG['COMPANY']['get_ptq_types_from_redis']['func'],
                    method=SERVICE_CONFIG['COMPANY']['get_ptq_types_from_redis']['method'],
                )
                if ptqTypesFromRedis:
                    ptqTypesFromRedis = json.loads(ptqTypesFromRedis)
                    ptqTypesFromRedis = ptqTypesFromRedis['data']
            except:
                ptqTypesFromRedis = []
            rule = [ptq_type for ptq_type in ptqTypesFromRedis if
                    ptq_type.get("deletedAt") is None and ptq_type.get("type")]
            rule_deadline = []
            rule_need = []
            rule_add = []
            for r in rule:
                if r['type'] == "NOTOK" or r['type'] == "CANCEL":
                    rule_deadline.append(r['id'])
                    rule_need.append(r['id'])
                if r['type'] == "ADD":
                    rule_need.append(r['id'])
                    rule_add.append(r['id'])

            flag = False
            for p in ptq:
                dln = datetime.strptime(p['deadline'], '%Y-%m-%d').date()
                if dln < date_from_now() or dln > date_from_now(1) or p['recorded'] not in rule_deadline:
                    if dln > date_from_now(-1) and p['recorded'] in rule_need:
                        flag = True
                        break
                    if p['recorded'] in rule_add:
                        flag = True
                        break
                    continue
                flag = True
                break

            if flag:
                self.showOrHideUserHomeTab(userId=userId, tabCode="cheTai", actionType="show", showForever="yes")
            else:
                self.showOrHideUserHomeTab(userId=userId, tabCode="cheTai", actionType="hide")

    def get_all_functions(self, request):
        try:
            functions_queryset = SettingFunctionIcons.objects.all()
            data_group_type = functions_queryset.filter(group_type__isnull=False).values_list('group_type', flat=True)
            functions = SettingFunctionIconsSerializer(functions_queryset, many=True).data
            user_info = getUserAuthSessionData(request.headers.get("Authorization"))
            user_permissions = user_info['permissions'].keys()
            function_messages = get_config("FUNCTION_STATUS_MESSAGES")

            for function in functions:
                function_permission = function['permissionCodes'].split(",")
                if "WORKING" != function['featureStatus']:
                    function["featureMessage"] = function_messages[function["featureStatus"]]
                    function['featureStatus'] = False
    
                elif not(
                    "ALL" 
                    in user_permissions
                    or bool(list(
                        set(function_permission) 
                        & set(user_permissions)
                    ))
                    or function_permission == ['']
                ):
                    function["featureMessage"] = function_messages["NO_PERMISSION"]
                    function['featureStatus'] = False
                else:
                    function["featureMessage"] = ""
                    function['featureStatus'] = True

            res_data = {
                "screenType": user_info.get("screenType", 0),
                "listGroup":list(set(data_group_type)),
                "functions": functions
            }
            return response_data(res_data)
        except Exception as e:
            print(e)
            return response_data(str(e), statusCode=4)

    def update_function(self, request):
        data = request.data
        title = data.get('title', None)
        try:
            data_update = SettingFunctionIcons.objects.get(icon_title=title)  # noqa
        except Exception:  # noqa
            return response_data(message="Function icon does not exist")
        try:
            serializer = SettingFunctionIconsSerializer(data_update, data=data, partial=True)
            if not serializer.is_valid():
                return response_data(message=serializer.errors)
            serializer.save()

            return response_data(message="Update function icon success")
        except Exception as ex:
            print(ex)
            return response_data(message="Update function icon fail")

    def add_function(self, request):
        data = request.data
        try:
            serializer = SettingFunctionIconsSerializer(data=data)

            if not serializer.is_valid():
                return response_data(message=serializer.errors)
            serializer.save()
            return response_data(message="Add function icon success")
        except Exception as ex:
            print(ex)
            return response_data(message="Add function icon fail")

    def remove_function(self, request):
        # Đây là xóa vĩnh viễn
        data = request.data
        title = data.get('title', None)
        try:
            data_remove = SettingFunctionIcons.objects.get(icon_title=title)  # noqa
        except Exception:  # noqa
            return response_data(message="Function icon does not exist")
        try:
            data_remove.delete()
        except Exception as ex:
            print("Error remove function icon:", ex)
            return response_data(message="Remove Function icon fail")
        return response_data(message="Remove Function icon success")

    def getShownTabsByUserId(self, userId, fullCurAppVerStr):
        query = "SELECT user_home_tab.tab_id, home_tab.tab_code, home_tab.tab_name, shown_start_date, shown_end_date, app_version FROM " + SettingUserHomeTabs._meta.db_table + " AS user_home_tab INNER JOIN " + SettingHomeTabs._meta.db_table + " AS home_tab ON home_tab.tab_id = user_home_tab.tab_id WHERE user_home_tab.user_id = " + str(
            userId) + " AND home_tab.is_deleted = 0 AND user_home_tab.is_shown = 1"
        cursor = connection.cursor()
        cursor.execute(query)
        userHomeTabsRows = cursor.fetchall()
        # return userHomeTabsRows
        if len(userHomeTabsRows) <= 0:
            return []

        tabs = []
        for userHomeTabRow in userHomeTabsRows:
            shownStartDate = userHomeTabRow[3]
            shownEndDate = userHomeTabRow[4]
            appVerStr = str(userHomeTabRow[5]).strip()
            tabPrefixToPrint = "[tab " + str(userHomeTabRow[0]) + " - " + userHomeTabRow[1] + "]"

            tabCanShow = False

            # Check fullCurAppVerStr so voi app_version (appVerStr)
            compareRes = self.compareAppVersions(fullCurAppVerStr, appVerStr)

            if compareRes == "LESS":
                print(
                    tabPrefixToPrint + " fullCurAppVer (" + fullCurAppVerStr + ") so voi appVer (" + appVerStr + ") : " + compareRes + " : Hien tai CHUA DEN version cho phep hien tab nay!")
                continue
            else:
                print(
                    tabPrefixToPrint + " fullCurAppVer (" + fullCurAppVerStr + ") so voi appVer (" + appVerStr + ") : " + compareRes + " : Hien tai da den version cho phep hien tab nay!")

            curTs = int(datetime.now().timestamp())
            if shownStartDate is None and shownEndDate is None:
                tabCanShow = True
                pass
            elif shownStartDate is not None and shownEndDate is not None:
                shownStartDateTs = int(shownStartDate.timestamp())
                shownEndDateTs = int(shownEndDate.timestamp())

                if curTs >= shownStartDateTs and curTs < shownEndDateTs:
                    print(tabPrefixToPrint + " curDate nam trong khoang startDate va endDate! Cho phep hien tab nay!")
                    tabCanShow = True
                else:
                    print(
                        tabPrefixToPrint + " curDate KHONG nam trong khoang startDate va endDate! KHONG cho phep hien tab nay!")

            elif shownStartDate is not None and shownEndDate is None:
                shownStartDateTs = int(shownStartDate.timestamp())

                if curTs >= shownStartDateTs:
                    tabCanShow = True
                else:
                    print(tabPrefixToPrint + " curDate nho hon startDate! KHONG CHO phep hien tab nay!")
            else:
                shownEndDateTs = int(shownEndDate.timestamp())

                if curTs < shownEndDateTs:
                    tabCanShow = True
                else:
                    print(tabPrefixToPrint + " curDate lon hon hoac bang endDate! KHONG CHO phep hien tab nay!")

            if tabCanShow == True:
                tabs.append({
                    "title": userHomeTabRow[2],
                    "id": userHomeTabRow[1]
                })

        return tabs

    def compareAppVersions(self, fullCurAppVerStr, appVerStr):
        # split 2 string nay theo dau cham
        appVerParts = appVerStr.split(".")
        if len(appVerParts) != 3:
            appVerParts.append("0")
        fullCurAppVerParts = fullCurAppVerStr.split(".")

        compareRes = "EQUAL"
        for partIndex, fullCurAppVerPart in enumerate(fullCurAppVerParts):
            subPrefix = "[compareAppVersions - curAppVer " + fullCurAppVerStr + " - appVer " + appVerStr + " - partIndex " + str(
                partIndex) + "]"
            appVerPart = int(appVerParts[partIndex])
            curAppVerPart = int(fullCurAppVerPart)
            if curAppVerPart == appVerPart:
                compareRes = "EQUAL"
                continue
            elif curAppVerPart > appVerPart:
                compareRes = "LARGER"
                return compareRes
            else:
                compareRes = "LESS"
                return compareRes

        return compareRes

    def validateAppVersion(self, latestAppVerInfo, currentAppVersion):
        # Get the current latest version of app & the latest version of user's app
        configValueStr = latestAppVerInfo['config_value'].strip()
        # Convert config value from string to dictionary
        configValueDict = json.loads(configValueStr)

        latestVersion = configValueDict['latestVer']
        forceUpdateData = None

        # It is impossible to have userVersion > currentVersion
        if currentAppVersion != latestVersion:
            today = datetime.now()
            dateStartNotification = datetime.strptime(configValueDict['dateStartNoti'], '%Y-%m-%d %H:%M:%S')
            # If the start date is earlier than the current date, nothing will happen.
            if today >= dateStartNotification:
                forceUpdateData = {
                    "isForced": int(configValueDict["isForced"]),
                    "lang": "vi",
                    "popupTitle": str(configValueDict["popupTitle"]),
                    "popupMsg": str(configValueDict["popupMsg"]),
                    "chPlayUrl": str(configValueDict["chPlayUrl"]),
                    "appStoreUrl": str(configValueDict["appStoreUrl"])
                }
        return forceUpdateData

    # API nay chi de goi private. API nay chi de cho service mypt-auth-api goi, trong t/h tao Access Token
    def assignDefaultTabsToUser(self, request):
        userId = request.data.get("userId", None)
        if userId is None:
            return response_data(None, 5, "Missing user id")

        userId = int(userId)
        if userId <= 0:
            return response_data(None, 5, "User id invalid")

        homeTabsQueryset = SettingHomeTabs.objects.filter(is_deleted=0, is_default=1)
        homeTabsSerializer = SettingHomeTabsSerializer(homeTabsQueryset, many=True)

        # tap hop cac home tab id
        homeTabIds = []
        for homeTab in homeTabsSerializer.data:
            homeTabIds.append(homeTab.get("tabId"))

        if len(homeTabIds) == 0:
            return response_data({"assignResult": 0, "reasonMsg": "No any home tab"})

        userHomeTabsQs = SettingUserHomeTabs.objects.filter(user_id=userId, tab_id__in=homeTabIds)
        userHomeTabsSerializer = SettingUsersHomeTabsSerializer(userHomeTabsQs, many=True)
        userHomeTabsRows = userHomeTabsSerializer.data
        userHomeTabIds = []
        for userHomeTabsRow in userHomeTabsRows:
            userHomeTabIds.append(userHomeTabsRow.get("tabId"))

        savedHomeTabIds = []
        for homeTabId in homeTabIds:
            if homeTabId not in userHomeTabIds:
                try:
                    with transaction.atomic():
                        userHomeTabsRecord = SettingUserHomeTabs(user_id=userId, tab_id=homeTabId, is_shown=1)
                        userHomeTabsRecord.save()
                        savedHomeTabIds.append(homeTabId)
                except IntegrityError as e:
                    print(e)
                    return response_data(None, statusCode=4,
                                         message="Error when save user permission to auth_user_permissions")
            else:
                print("home tab " + str(homeTabId) + " da duoc assign cho userId " + str(
                    userId) + " roi nen ko can add nua!")

        return response_data({"assignResult": 1, "savedHomeTabIds": savedHomeTabIds})

    # API nay chi de goi private. API nay se do mypt-checkin-api goi
    def updateShownStartDateUsersHomeTabs(self, request):
        userId = request.data.get("userId", None)
        if userId is None:
            return response_data(None, 5, "Missing user id")

        userId = int(userId)
        if userId <= 0:
            return response_data(None, 5, "User id invalid")

        tabCode = request.data.get("tabCode", None)

        homeTabsQueryset = SettingHomeTabs.objects.filter(is_deleted=0, tab_code=tabCode)
        if not homeTabsQueryset.exists():
            return response_data(None, 6, "Home tab " + tabCode + " does not exist or deleted!")

        homeTabsSerializer = SettingHomeTabsSerializer(homeTabsQueryset, many=True)
        homeTabId = int(homeTabsSerializer.data[0].get("tabId", None))

        userHomeTabsRecord = SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId)
        if not userHomeTabsRecord.exists():
            return response_data(None, statusCode=6, message="Not found user home tab !")

        newShownStartDate = self.getTomorrowDateTime()
        try:
            with transaction.atomic():
                userHomeTabsRecord.update(shown_start_date=newShownStartDate,
                                          date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except IntegrityError as e:
            print(e)
            return response_data(None, statusCode=4,
                                 message="Error when update shown start date to setting_users_home_tabs")
        return response_data(None, 1, "Updated shown start date success!")

    # API nay chi de goi private. API nay truoc mat se do service Che Tai goi
    def showHideUserHomeTab(self, request):
        # Uu tien check param userId truoc, sau do moi check param email
        userId = request.data.get("userId", None)
        if userId is None:
            emailStr = request.data.get("email", None)
            if emailStr is None:
                return response_data(None, 5, "Missing user id and email")

            # Goi qua mypt-auth-api de lay userId theo email nay
            authApis = MyPtAuthApis()
            resGetCreateUser = authApis.getOrCreateUserByEmail(emailStr)
            if resGetCreateUser is None:
                return response_data(None, 6, "Get or create user by email failed")
            userId = int(resGetCreateUser.get("userId", 0))
            if userId <= 0:
                return response_data(None, 6, "User not found by email")
            # return response_data({"finalUserId": userId})
        else:
            userId = int(userId)
            if userId <= 0:
                return response_data(None, 5, "User id invalid")

        tabCode = request.data.get("tabCode", None)
        if tabCode is None:
            return response_data(None, 5, "Missing tab code")
        tabCode = str(tabCode).strip()
        if tabCode == "":
            return response_data(None, 5, "Tab code is empty")

        actionType = request.data.get("actionType", "")
        if actionType not in ["show", "hide"]:
            return response_data(None, 5, "Action type is invalid because action type is : " + actionType)

        # return response_data({"userId": userId, "tabCode": tabCode, "loaiHD": actionType})
        isShown = 0
        if actionType == "show":
            isShown = 1

        showForever = ""
        if isShown == 1:
            showForever = request.data.get("showForever", "yes")
            if showForever not in ["yes", "no"]:
                return response_data(None, 5, "Param showForever is invalid")

        homeTabsQueryset = SettingHomeTabs.objects.filter(tab_code=tabCode, is_deleted=0)
        if not homeTabsQueryset.exists():
            return response_data(None, 6, "Home tab " + tabCode + " does not exist or deleted!")

        homeTabsSerializer = SettingHomeTabsSerializer(homeTabsQueryset, many=True)
        homeTabId = int(homeTabsSerializer.data[0].get("tabId", None))

        # return response_data({"userId": userId, "tabCode": tabCode, "homeTabId": homeTabId, "loaiHD": actionType, "showForever": showForever})

        userHomeTabsRecord = SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId)
        if not userHomeTabsRecord.exists():
            # Insert 1 dong users_home_tabs cho userId & homeTabId
            if isShown == 1:
                print("INSERT : can show tab!")
            else:
                print("INSERT : KHONG can show tab!")
            newUserHomeTabsRecord = SettingUserHomeTabs()
            newUserHomeTabsRecord.user_id = userId
            newUserHomeTabsRecord.tab_id = homeTabId
            newUserHomeTabsRecord.is_shown = isShown
            newUserHomeTabsRecord.shown_start_date = None
            newUserHomeTabsRecord.shown_end_date = None
            newUserHomeTabsRecord.save()
        else:
            # update
            if isShown == 1 and showForever == "yes":
                rowsUpdated = SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId).update(
                    is_shown=isShown, shown_start_date=None, shown_end_date=None,
                    date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                rowsUpdated = SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId).update(
                    is_shown=isShown, date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return response_data(None, 1, "Show/hide success!")

    def getTomorrowDateTime(self):
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        # tomorrowDateTime = datetime.combine(tomorrow, datetime.time(0, 0, 0))

        tomorrowDateTimeStr = tomorrow.strftime("%Y-%m-%d") + " 00:00:01"
        return tomorrowDateTimeStr

    def showOrHideUserHomeTab(self, userId, tabCode="cheTai", actionType="show", showForever="no"):
        if userId <= 0:
            print("User not found by email")
            return
        # return response_data({"finalUserId": userId})

        if tabCode is None:
            print("Missing tab code")
            return

        tabCode = str(tabCode).strip()
        if tabCode == "":
            print("Tab code is empty")
            return

        if actionType not in ["show", "hide"]:
            print("Action type is invalid because action type is : " + actionType)
            return

        # return response_data({"userId": userId, "tabCode": tabCode, "loaiHD": actionType})
        isShown = 0
        if actionType == "show":
            isShown = 1

        if isShown == 1:
            if showForever not in ["yes", "no"]:
                print("Param showForever is invalid")
                return

        homeTabsQueryset = SettingHomeTabs.objects.filter(tab_code=tabCode, is_deleted=0)
        if not homeTabsQueryset.exists():
            print("Home tab " + tabCode + " does not exist or deleted!")
            return

        homeTabsSerializer = SettingHomeTabsSerializer(homeTabsQueryset, many=True)
        homeTabId = int(homeTabsSerializer.data[0].get("tabId", None))

        # return response_data({"userId": userId, "tabCode": tabCode, "homeTabId": homeTabId, "loaiHD": actionType, "showForever": showForever})

        userHomeTabsRecord = SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId)
        if not userHomeTabsRecord.exists():
            # Insert 1 dong users_home_tabs cho userId & homeTabId
            if isShown == 1:
                print("INSERT : can show tab!")
            else:
                print("INSERT : KHONG can show tab!")
            newUserHomeTabsRecord = SettingUserHomeTabs()
            newUserHomeTabsRecord.user_id = userId
            newUserHomeTabsRecord.tab_id = homeTabId
            newUserHomeTabsRecord.is_shown = isShown
            newUserHomeTabsRecord.shown_start_date = None
            newUserHomeTabsRecord.shown_end_date = None
            newUserHomeTabsRecord.save()
        else:
            userHomeTabsSr = SettingUsersHomeTabsSerializer(userHomeTabsRecord, many=True)
            userHomeTabData = userHomeTabsSr.data[0]
            print("userHomeTabData co : ")
            print(userHomeTabData)
            # update
            if isShown == 1 and showForever == "yes":
                print("Updated : can show tab va show forever!")
                if userHomeTabData["isShown"] == 0 or userHomeTabData["shownStartDate"] is not None or userHomeTabData[
                    "shownEndDate"] is not None:
                    SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId).update(is_shown=1,
                                                                                                shown_start_date=None,
                                                                                                shown_end_date=None,
                                                                                                date_modified=datetime.now().strftime(
                                                                                                    "%Y-%m-%d %H:%M:%S"))
                else:
                    print("Updated: is_shown da la 1 va cac Date da la None roi nen ko can update nua!")
            else:
                print("Updated : KHONG can show tab ; hoac can show tab va ko show forever!")
                if isShown == 0:
                    if userHomeTabData["isShown"] == 1:
                        SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId).update(is_shown=0,
                                                                                                    date_modified=datetime.now().strftime(
                                                                                                        "%Y-%m-%d %H:%M:%S"))
                    else:
                        print("Updated: is_shown da la 0 roi nen ko can update nua!")
                else:
                    if userHomeTabData["isShown"] == 0:
                        SettingUserHomeTabs.objects.filter(user_id=userId, tab_id=homeTabId).update(is_shown=1,
                                                                                                    date_modified=datetime.now().strftime(
                                                                                                        "%Y-%m-%d %H:%M:%S"))
                    else:
                        print("Updated: is_shown da la 1 roi nen ko can update nua!")

    def getPtqTypesFromRedis(self):
        redisInstance = redis.StrictRedis(host=project_settings.SERVICE_REDIS_HOST,
                                          port=project_settings.SERVICE_REDIS_PORT,
                                          db=project_settings.SETTING_REDIS_DATABASE,
                                          password=project_settings.SERVICE_REDIS_PASSWORD,
                                          decode_responses=True, charset="utf-8")

        ptqTypeStr = redisInstance.get("ptqTypes")
        if ptqTypeStr is None:
            print("can tao lai Redis cho PTQ types!")
            qs = PtqType.objects.all()
            serializer = PtqTypeSerializer(qs, many=True)
            rows = serializer.data
            dataForRedis = []
            for row in rows:
                dataForRedis.append({"id": row.get("id"), "type": row.get("type"), "deletedAt": row.get("deletedAt")})
            resSaveRedis = redisInstance.set("ptqTypes", str(dataForRedis), 86400)
            return dataForRedis
        else:
            print("DA TON TAI Redis ptq types !")
            ptqTypeData = ast.literal_eval(ptqTypeStr)
            return ptqTypeData

    def remove_setting_config(self, request):
        try:
            data = request.data.copy()
            if "config_key" not in data:
                return response_data("no_config_key", status=4)

            config_key = data["config_key"]
            remove_config(config_key)
            return response_data()
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))

    def get_setting_config(self, request):
        try:
            data = request.data.copy()
            if "config_key" not in data:
                return response_data("no_config_key", status=4)

            config_key = data["config_key"]

            return response_data(get_config(config_key))
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))

    def _check_survey(self, token):
        try:
            response = requests.request(**get_api_info("survey", "scrutiny"), headers={"Authorization": token})
            return response.json()["status"] == 1
        except Exception as e:
            print(e)
            return False