import ast
from datetime import timedelta

import redis
from django.db import connection
from django.db import transaction

from ..models.agency_and_province import AgencyAndProvince
from ..serializers.agency_and_province_serializer import AgencyAndProvinceSerializer
from django.db.models import Avg
from django.db.models import Q, F
from rest_framework import status
from rest_framework.viewsets import ViewSet

from mypt_profile.settings import APP_ENVIRONMENT
from ..models.agency_and_province import AgencyAndProvince
from ..models.features_roles import FeaturesRoles
from ..models.features_roles_emails import FeaturesRolesEmails
# from ..models.employees_tb import EmployeesTb
# from ..models.profile import EmployeesTb
from ..models.screen import Screen
from ..paginations.custom_pagination import *
from ..serializers.agency_and_province_serializer import AgencyAndProvinceSerializer
from ..serializers.configs_serializer import *
from ..serializers.contract_serializer import *
from ..serializers.department_serializer import DepartmentsSerializer
from ..serializers.employee_serializer import *
from ..serializers.provinces_and_regions_serializer import *
from ..serializers.safe_card_serializer import *
from ..serializers.user_profile_serializer import *
from ...configs.variable import *
from ...core.helpers import auth_session_handler as authSessionHandler
from ...core.helpers import global_data
from ...core.helpers.helper import *
from ...core.helpers.response import *
# GHI LOG
from ...core.helpers.utils import *
from ...http.models.profile import *
from ...http.validations.profile_validate import *


class ProfileView(ViewSet):
    cache = {}
    userInfo = {}
    pagination_class = CustomPagination()

    def check_user_info_my_profile(self, request):
        self.userInfo = authSessionHandler.get_user_token(request)
        if self.userInfo is None:
            self.userInfo = {}

        try:
            fake_config = ProfileConfigSerializer.get_value_by_key("MY_PROFILE_FAKE_INFO")

            if self.userInfo:
                email = self.userInfo.get("email", "")
                if not (is_empty(email) or is_empty(fake_config)):
                    fake_config = json.loads(fake_config)

                    if email in fake_config and not is_empty(fake_config[email]):
                        employee = Employee.objects.filter(email=fake_config[email]).first()
                        if employee:
                            self.userInfo["email"] = fake_config[email]
                            self.userInfo["empCode"] = employee.emp_code
                            self.userInfo["childDepart"] = employee.child_depart
        except Exception as ex:
            print(f"{datetime.now()} >> check_user_info_my_profile >> {ex}")

    def check_show_data_employee(self, job_title, action):
        try:
            if job_title in [emp_position for emp_position in EMPLOYEE_POSITION]:
                if EMPLOYEE_POSITION[job_title][action]:
                    return True
        except Exception as ex:
            print(f"{datetime.now()} >> check_show_data_employee >> {ex}")
        return False

    def get_employee_info(self, request):
        userPersData = authSessionHandler.get_user_token(request)

        data_output = {
            "empCode": "---",
            "userId": "---",
            "agency": "---",
            "childDepart": "--",
            "parentDepart": "---",
            "jobTitle": "---",

            "name": "---",
            "avatarImg": "---",
            "sex": "---",
            "email": "---",
            "branch": "---",
            "salaryMessage": "",
            "salary": None,
        }

        try:
            email = userPersData.get("email", None)
            if email is None:
                return response_data(data=data_output, status=3, message="Token không hợp lệ")

            branch = userPersData.get("branch", "")
            if branch is None or branch == "":
                branch = "FTEL"

            userId = userPersData.get("userId", "---")
            name = userPersData.get("fullName", "---")

            code = userPersData.get("empCode", "---")
            agency = userPersData.get("agency", "---")
            childDepart = userPersData.get("childDepart", "---")
            parentDepart = userPersData.get("parentDepart", "---")
            jobTitle = userPersData.get("jobTitle", "---")
            sex = userPersData.get("sex")
            # avatarImg = userPersData.get("userAvatarUrl", "")
            avatarImg = MyInfoUserProfileSerializer.get_avarta_from_user_id(userId)
            if avatarImg == "" or avatarImg is None:
                if sex == "F":
                    avatarImg = AVATAR_DEFAULT["female"]
                else:
                    avatarImg = AVATAR_DEFAULT["male"]

            data_output = {
                "userId": userId,

                "empCode": code,
                "agency": agency,
                "childDepart": childDepart,
                "parentDepart": parentDepart,
                "jobTitle": jobTitle,
                "name": name,
                "avatarImg": avatarImg,
                "sex": sex,
                "email": email,
                "branch": branch,
                "salaryMessage": "",
                "salary": None,
            }
            return response_data(data=data_output, status=1, message="Success")

        except Exception as _:
            return response_data(data=data_output, status=3, message="Token expired")

    def get_employee_info_new(self, request):
        func_name = "get_employee_info_new"
        userPersData = authSessionHandler.get_user_token(request)

        try:
            if userPersData and userPersData.get("email", None) is not None:
                email = userPersData["email"]
            else:
                raise ValueError("Token expired")
        except:
            return response_data(status=3, message="Token expired")
        if "phuongnam" in email:
            branch = "PNC"
        elif "vienthongtin" in email:
            branch = "TIN"
        else:
            branch = "FTEL"
        try:
            data_redis = userPersData
            name = data_redis["fullName"]
        except:
            name = "---"
        try:
            code = data_redis["empCode"]
        except:
            code = "---"
        try:
            token_hr = hr_auth()
            dataApi = get_employee_info_from_hris(token=token_hr, email=email)
        except:
            dataApi = {}

        try:
            pk = self.get_emp_code(email)
            if pk:
                pk = pk.get("emp_code", None)

            data = {}
            if pk:
                data = self.get_employee(pk)
            else:
                if not is_empty(email):
                    fields = ["avatarImg"]
                    user_profile_data = self.get_user_profile_with_email(email=email, fields=fields)
                    data['avatarImg'] = user_profile_data["avatarImg"]
            # print("data: ", data)
            if data['avatarImg'] is not None and data['avatarImg'] != "" \
                    and data['avatarImg'].startswith(("http://", "https://")):
                avatarImg = data['avatarImg']
            elif data["sex"] == "M":
                avatarImg = AVATAR_DEFAULT["male"]
            else:
                avatarImg = AVATAR_DEFAULT["female"]
        except:
            avatarImg = AVATAR_DEFAULT["male"]
        try:
            # if data["name"] is not None and data['name'] != "":
            #     dataApi["fullName"] = data["name"]
            #     print(data)
            dataApi['fullName'] = name
            if data["empCode"] is not None and data['empCode'] != "":
                code = data["empCode"]
        except:
            dataApi['fullName'] = name
        #  lay thong tin gioi tinh
        try:
            sex = data["sex"]
        except:
            sex = ""

        # Lay thong tin luong tu service mypt-job-api
        salary_data = get_salary_in_home(request)
        if salary_data:
            if salary_data["statusCode"] == 1:
                salary = salary_data["data"]
            else:
                salary = None
                print(f'[{datetime.now()}][{func_name}]: {salary_data["message"]}')
        else:
            salary = None
            print(f'[{datetime.now()}][{func_name}]: co loi khi lay thong tin luong tu mypt-job-api')

        data = {
            "empCode": code,
            "name": dataApi.pop("fullName", "---"),
            "avatarImg": avatarImg,
            "sex": sex,
            "salary": salary,
            "email": email,
            "branch": branch
        }
        return response_data(data=data)

    def email_to_list_code(self, request):
        data = request.data
        validate = ListEmpCodeValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message="error", data=validate.errors)
        queryset = Employee.objects.filter(emp_code__in=data["empCode"])
        serializer = EmployeeSerializer(queryset, many=True, fields=["email", "code"])
        return response_data(serializer.data)

    def info_to_email(self, request):
        if 'email' not in request.data:
            return response_data(status=5, message='email is valid')
        code = dict(self.get_emp_code(email=request.data["email"]))
        data = self.get_employee(code=code['emp_code'])
        name = convert_vi_to_en(data['name'])
        name = name.split()
        data["imageDefault"] = name[0][0] + name[-1][0]
        if data['avatarImg'] is not None:
            data['avatarImg'] = AVATAR['host'] + data['avatarImg'] + AVATAR['type']
        return response_data(data)

    def get_employee_from_email(self, request):
        try:
            data = request.data
            if "email" in data and not is_empty(data["email"]):
                email = data["email"]
                fields = data.get("fields", None)
                queryset = Employee.objects.filter(email=email)
                if fields is not None:
                    serializer = EmployeeSerializer(queryset, many=True, fields=fields)
                else:
                    serializer = EmployeeSerializer(queryset, many=True)
                if len(serializer.data) > 0:
                    return response_data(data=serializer.data[0])
                return response_data(data=None, message="Không tìm thấy thông tin nhân viên!")
            else:
                return response_data(status=5, message="Email không hợp lệ!", data=None)
        except Exception as ex:
            print(f"{datetime.now()} >> get_employee_from_email >> {ex}")
            return response_data(data=None, status=4, message=f"Lỗi hệ thống {ex}")

    # API nay chi de goi private. API nay chi de cho service mypt-auth-api goi, trong t/h tao Access Token
    def check_get_employee(self, request):
        try:
            email = request.data['email']
            email = email.lower()
            userId = request.data['userId']
            fullName = request.data['fullName']
            specificChildDeparts = request.data.get("specificChildDeparts", [])

            # check screen TPL
            screen_value = self.is_TPL(email=email)

            # Tim xem userId nay co profile hay chua
            profileQs = UserProfile.objects.filter(user_id=userId)[0:1]
            profileSer = UserProfileSerializer(profileQs, many=True)
            profileArrs = profileSer.data

            newUserProfile = None
            if len(profileArrs) <= 0:
                is_has_profile = False
                # print("Chuan bi tao user profile cho userId " + str(userId))
                # Neu chua co profile : tao profile cho userId nay
                newUserProfile = UserProfile()
                newUserProfile.user_id = userId
                newUserProfile.email = email
                newUserProfile.full_name = fullName
                newUserProfile.save()
            else:
                is_has_profile = True
                # print("Da ton tai user profile cua userId " + str(userId))

            # xu ly specificChildDeparts
            branchParentDepartsData = {}
            if len(specificChildDeparts) > 0:
                childDepartsQs = Department.objects.filter(child_depart__in=specificChildDeparts)
                childDepartsSer = DepartmentSerializer(childDepartsQs, many=True)
                departRows = childDepartsSer.data
                if len(departRows) > 0:
                    for departRow in departRows:
                        childDepartStr = departRow.get("childDepart")
                        branchParentDepartsData[childDepartStr] = {
                            "parentDepart": departRow.get("parentDepart"),
                            "branch": departRow.get("branch")
                        }
                else:
                    branchParentDepartsData = None
            else:
                branchParentDepartsData = None

            # lay thong tin features roles cua email nay
            feaRolesData = self.getFeaturesRolesByEmail(email)

            # Tim thong tin employee dua theo email
            queryset = Employee.objects.filter(email=email)
            serializer = EmployeeSerializer(queryset, many=True)

            if len(serializer.data) <= 0:
                # print("Khong tim thay row employee cua email : " + email)
                return response_data({
                    "isTinPncEmployee": 0,
                    "childDepart": "",
                    "parentDepart": "",
                    "agency": "",
                    "isHO": 0,
                    "branch": "",
                    "empCode": "",
                    "jobTitle": "",
                    "empContractType": "",
                    "branchParentDeparts": branchParentDepartsData,
                    "birthday": "",
                    "sex": "",
                    "featuresRoles": feaRolesData,
                    "userAvatarUrl": "",
                    "screenType": screen_value
                })

            # CAP NHAT THONG TIN PROFILE TAI DAY
            try:
                employee_serializer = serializer.data[0]
                if is_has_profile:
                    # da ton tai profile
                    current_user_profile = profileQs[0]
                    is_save = False
                    if is_empty(current_user_profile.birthday):
                        current_user_profile.birthday = employee_serializer["birthday"]
                        is_save = True
                    if is_empty(current_user_profile.sex):
                        current_user_profile.sex = employee_serializer["sex"]
                        is_save = True
                    if is_empty(current_user_profile.mobile_phone):
                        current_user_profile.mobile_phone = employee_serializer["mobilePhone"]
                        is_save = True
                    if is_empty(current_user_profile.place_of_birth):
                        current_user_profile.place_of_birth = employee_serializer["placeOfBirth"]
                        is_save = True
                    if is_empty(current_user_profile.nationality):
                        current_user_profile.nationality = employee_serializer["nationality"]
                        is_save = True
                    if current_user_profile.marital_status is None:
                        current_user_profile.marital_status = employee_serializer["maritalStatus"]
                        is_save = True
                    if is_save:
                        current_user_profile.save()
                    newUserProfile = current_user_profile
                else:
                    # profile moi
                    # UserProfile.objects.filter(user_id=userId).update(birthday=employee_serializer["birthday"],
                    #                                                   sex=employee_serializer["sex"],
                    #                                                   mobile_phone=employee_serializer["mobilePhone"],
                    #                                                   place_of_birth=employee_serializer[
                    #                                                       "placeOfBirth"],
                    #                                                   nationality=employee_serializer["nationality"],
                    #                                                   marital_status=employee_serializer[
                    #                                                       "maritalStatus"])
                    # newUserProfile.birthday = employee_serializer["birthday"]
                    _birthday = datetime.strptime(employee_serializer["birthday"], "%d/%m/%Y")
                    str_birthday = datetime.strftime(_birthday, "%Y-%m-%d")
                    newUserProfile.birthday = str_birthday

                    newUserProfile.sex = employee_serializer["sex"]
                    newUserProfile.mobile_phone = employee_serializer["mobilePhone"]
                    newUserProfile.place_of_birth = employee_serializer["placeOfBirth"]
                    newUserProfile.nationality = employee_serializer["nationality"]
                    newUserProfile.marital_status = employee_serializer["maritalStatus"]
                    newUserProfile.save()
            except Exception as ex:
                print(f"{datetime.now()} >> cap nhat profile tu employee >> {ex}")

            empData = serializer.data[0]

            # xu ly avatar
            try:
                gender = newUserProfile.sex
                avatar = newUserProfile.avatar_img

                if avatar and avatar != "" \
                        and avatar.startswith(("http://", "https://")):
                    avatar_img = avatar
                elif gender == "M":
                    avatar_img = AVATAR_DEFAULT["male"]
                elif gender == "F":
                    avatar_img = AVATAR_DEFAULT["female"]
                else:
                    raise Exception("Không có avatar và không phân biệt được giới tính.")
            except Exception as ex:
                avatar_img = AVATAR_DEFAULT["male"]
                print(f"{datetime.now()} >> xy ly avatar >> {ex}")

            # check job_title is TPL
            screen_value = self.job_title_TPL(empData["jobTitle"])

            # chuan bi data de response
            profileData = {
                "isTinPncEmployee": 1,
                "childDepart": empData["childDepart"],
                "parentDepart": "",
                "isHO": 0,
                "branch": "",
                "empCode": empData["code"],
                "jobTitle": empData["jobTitle"],
                "empContractType": "",
                "branchParentDeparts": branchParentDepartsData,
                "birthday": newUserProfile.birthday if newUserProfile and not is_empty(newUserProfile.birthday) else "",
                "sex": newUserProfile.sex if newUserProfile and not is_empty(newUserProfile.sex) else "",
                "featuresRoles": feaRolesData,
                "contractType": "",
                "userAvatarUrl": avatar_img,
                "screenType": screen_value
            }

            # set gia tri cho empContractType
            emp_con_type = str(empData["contractType"])
            empConTypeToCheck = emp_con_type.lower()
            # print("emp contract type luc dau : " + emp_con_type + " ; luc sau : " + empConTypeToCheck)
            if empConTypeToCheck in CONTRACT_TYPE['new']:
                # print("day la nhan vien new")
                profileData['empContractType'] = 'new'
            else:
                # print("day la nhan vien official")
                profileData['empContractType'] = 'official'

            profileData['contractType'] = empConTypeToCheck
            # tim Department dua theo child_depart
            departQs = Department.objects.filter(child_depart=empData["childDepart"])[0:1]
            departSer = DepartmentSerializer(departQs, many=True)
            departArrs = departSer.data
            if len(departArrs) <= 0:
                # print("Khong tim thay department theo code : " + empData["childDepart"])
                return response_data(None, 6, "Depart not found")

            departData = departArrs[0]
            # print("Da tim thay branch cua depart " + empData["childDepart"] + " : " + departData["parentDepart"] +
            # " : " + departData["branch"])
            profileData["parentDepart"] = departData["parentDepart"]
            profileData["branch"] = departData["branch"]
            profileData["agency"] = departData["agency"] if departData["agency"] else ""

            if profileData["parentDepart"] == "PNCHO" or profileData["parentDepart"] == "TINHO":
                profileData["isHO"] = 1

            print(profileData)
            return response_data(profileData)
        except Exception as e:
            print(e)
            return response_data(data={}, message=str(e), status=0)

    def is_TPL(self, email, screen_key='TPL'):
        screen_value = SCREEN.get('default', 0)
        screen_data = Screen.objects.filter(deleted_at__isnull=True, group=screen_key).values_list('email', flat=True)
        print(screen_data)
        if email in screen_data:
            return SCREEN.get(screen_key, 1)
        return screen_value

    def job_title_TPL(self, job_title, screen_key='TPL'):
        screen_value = SCREEN.get('default', 0)
        try:
            config = self.get_config_model(screen_key)
            serializer = ProfileConfigSerializer(config)
            config_data = serializer.data['configValue']
            my_set = ast.literal_eval(config_data)
            if job_title in my_set:
                return SCREEN.get(screen_key, 1)
            return screen_value
        except:
            return screen_value

    def get_config_model(self, config_key):
        obj, created = ProfileConfig.objects.get_or_create(
            config_key=config_key,
            defaults={
                'config_key': config_key,
                'config_value': str(CONFIGS_KEY[config_key])
            }
        )
        return obj

    def getFeaturesRolesByEmail(self, email):
        email = email.lower()
        query = "SELECT fea_role.role_code, fea_role.feature_code FROM " + FeaturesRolesEmails._meta.db_table + " AS fea_role_email INNER JOIN " + FeaturesRoles._meta.db_table + " AS fea_role ON fea_role_email.role_id = fea_role.role_id WHERE fea_role_email.email = \"" + email + "\" AND fea_role.platform = \"app\""
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        feaRoles = {}
        for row in rows:
            feaRoles[row[1]] = row[0]
        return feaRoles

    def get_employee(self, code=None):
        try:
            queryset = Employee.objects.get(emp_code=code)
            serializer = EmployeeSerializer(queryset)
            return serializer.data
        except:
            return None

    def get_employee_info_with_emp_code(self, emp_code, fields=None):
        try:
            queryset = Employee.objects.get(emp_code=emp_code)
            serializer = MyInfoEmployeeSerializer(queryset)
            if fields is not None:
                serializer = MyInfoEmployeeSerializer(queryset, fields=fields)
            return serializer.data
        except Exception as ex:
            print(f"{datetime.now()} >> get_employee_info_with_emp_code >> {ex}")
            return None

    def get_user_profile_with_email(self, email, fields=None):
        try:
            queryset = UserProfile.objects.filter(email=email).first()
            if queryset is None:
                raise Exception("queryset is null")

            serializer = MyInfoUserProfileSerializer(queryset)
            if fields is not None:
                serializer = MyInfoUserProfileSerializer(queryset, fields=fields)
            return serializer.data
        except Exception as ex:
            print(f"{datetime.now()} >> get_user_profile_with_email >> {ex}")
            return None

    def get_rank(self, pk):
        try:
            queryset = EmployeeRank.objects.filter(emp_code=pk).order_by('-update_time')
            serializer = EmployeeRankSerializer(queryset, many=True, fields=["rank"])
            data = ""
            if serializer.data != []:
                data = str(serializer.data[0])
            return data
        except:
            return ""

    def get_employee_code(self, request):
        try:
            email = self.get_email_from_token(request)
            code = self.get_emp_code(email=email)
            return code['emp_code']
        except:
            return None

    def get_emp_code(self, email=None):
        try:
            queryset = Employee.objects.get(email=email)
            serializer = CodeEmployeeSerializer(queryset)
            return serializer.data
        except:
            return None

    def get_email_from_token(self, request):
        try:
            return authSessionHandler.get_user_token(request).get("email", None)
        except Exception as ex:
            print(f"{datetime.now()} >> get_email_from_token >> {ex}")
            return None

    def get_info_from_token(self, request):
        try:
            return authSessionHandler.get_user_token(request)
        except Exception as ex:
            print(f"{datetime.now()} >> get_info_from_token >> {ex}")
            return None

    def date_format(self, data):
        if len(data.day) < 2:
            day = "0" + str(data.day)
        else:
            day = data.day
        if len(data.month) < 2:
            month = "0" + str(data.month)
        else:
            month = data.month
        return str(day) + "/" + str(month) + "/" + str(data.year)

    def health_check(self, request):

        # test lay domain name tu request
        domainName = request.get_host()

        # test ket noi mysql db
        try:
            queryset = Employee.objects.all()
            count = Employee.objects.count()
            paginator = StandardPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = EmployeeSerializer(result, many=True)
            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                'newsList': serializer.data
            }
            # print('data ok')
            # print(data)
        except Exception as ex:
            print(f"{datetime.now()} >> health_check >> {ex}")
            return Response({'statusCode': 0, 'message': 'data connection not ok', 'data': ex}, status.HTTP_200_OK)

        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("profile", "Day la value cua Redis key myptProfile abcdef 123969jkl", 3600)
        # print("redis value : " + redisInstance.get("profile"))
        #
        # print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
        # print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
        # print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

        resData = {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "myptProfileRedisVal": redisInstance.get("profile"),
            "domainName": domainName
        }

        return response_data(data=resData)

    def get_setting_config_by_key(self, key):
        # profile_config = ProfileConfig.objects.filter(config_key=key).first()
        # if profile_config:
        #     profile_config_serializer = ProfileConfigSerializer(profile_config)
        #     return profile_config_serializer.data
        # return {}
        try:
            app_env = "base_http_" + APP_ENVIRONMENT

            response = call_api(
                host=SERVICE_CONFIG["setting-api"][app_env],
                func=SERVICE_CONFIG["setting-api"]["get_code"]["func"],
                method=SERVICE_CONFIG["setting-api"]["get_code"]["method"],
                data={
                    "config_key": key,
                }
            )
            return json.loads(response)
        except Exception as ex:
            print("{} >> {} >> {}".format(datetime.now(), "get_setting_config_by_key", ex))
            return None

    # def get_checkin_location_from_id(self, building_office_id, fields=None):
    #     checkin_location_queryset = CheckinLocation.objects.filter(building_office_id=building_office_id,
    #                                                                status_working=1).first()
    #
    #     if fields:
    #         serializer = CheckinLocationSerializer(checkin_location_queryset, fields=fields)
    #     else:
    #         serializer = CheckinLocationSerializer(checkin_location_queryset)
    #
    #     return serializer.data

    def get_info_checkin_from_emp_code(self, employee_code):
        try:
            emp_contract_type = self.userInfo.get("empContractType", "")

            app_env = "base_http_" + APP_ENVIRONMENT
            response = call_api(
                host=SERVICE_CONFIG["checkin-api"][app_env],
                func=SERVICE_CONFIG["checkin-api"]["get_code"]["func"],
                method=SERVICE_CONFIG["checkin-api"]["get_code"]["method"],
                data={
                    "empCode": employee_code,
                    "typeEmp": emp_contract_type
                }
            )
            return json.loads(response)
        except Exception as ex:
            print(f"{datetime.now()} >> get_info_checkin_from_emp_code >> {ex}")
            return None

    def get_user_devices_info_by_email(self, email):
        try:
            app_env = "base_http_" + APP_ENVIRONMENT
            # print("APP_ENVIRONMENT là: ", APP_ENVIRONMENT)
            response = call_api(
                host=SERVICE_CONFIG["auth-api"][app_env],
                func=SERVICE_CONFIG["auth-api"]["GetUserDeviceInfoByEmail"],
                method=SERVICE_CONFIG["auth-api"]["method"],
                data={
                    "email": email
                }
            )
            return json.loads(response)
        except Exception as ex:
            print(f"{datetime.now()} >> get_user_devices_info_by_email >> {ex}")
            return None

    def getEmployeeLevel(self, emp_code=None):
        try:
            lst_month = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]

            today = datetime.today().date()
            year = today.year
            month = today.month
            if month in lst_month[0]:
                lst_month_search = lst_month[3]
                year -= 1
            elif month in lst_month[1]:
                lst_month_search = lst_month[0]
            elif month in lst_month[2]:
                lst_month_search = lst_month[1]
            else:
                lst_month_search = lst_month[2]
            bac_nghe = EmployeeRank.objects.filter(
                emp_code=emp_code, thang__in=lst_month_search, nam=year).aggregate(Avg('bac_nghe'))
            bac_nghe_response = round(bac_nghe['bac_nghe__avg']) if bac_nghe['bac_nghe__avg'] is not None else None
            return bac_nghe_response
        except Exception as ex:
            print(f"{datetime.now()} >> getEmployeeLevel >> {ex}")
        return None

    def update_situation_safe_card(self, request=None):
        try:
            today = datetime.now().date()
            day_45 = today + timedelta(days=45)

            queryset = SafeCard.objects.exclude(
                tinh_trang_the_chung_chi__in=["Hết Hạn", "Chưa Cấp"]
            )
            queryset.filter(ngay_het_han_ATLD__lte=today).update(
                tinh_trang_the_chung_chi="Hết Hạn")
            queryset.filter(ngay_het_han_ATLD__lte=day_45, ngay_het_han_ATLD__gt=today).update(
                tinh_trang_the_chung_chi="Sắp Hết Hạn")

            return response_data()
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))

    def get_email_list_from_branch(self, request):
        data = request.data

        if "branch" in data \
                and data.get("branch") \
                and data.get("branch") != "":
            branch = data["branch"]
            department = Department.objects
            if branch == "ALL":
                department = department.exclude(Q(branch=None) | Q(branch="")).all()
            elif branch == "TIN":
                department = department.filter(branch=branch).all()
            elif branch == "PNC":
                department = department.filter(branch=branch).all()
            else:
                return response_data(status=5, message="branch không hợp lệ!")

            child_depart_list = department.values_list('child_depart')
            child_depart_list = [x[0] for x in child_depart_list]

            employee_data = Employee.objects.filter(child_depart__in=child_depart_list, status_working=1)
            employee_serializer = EmployeeSerializer(employee_data, many=True, fields=["email"])

            email_list = [x["email"] for x in employee_serializer.data]

            return response_data(data=email_list)

        else:
            return response_data(status=5, message="branch là bắt buộc và không được rỗng!")

    def get_list_email_by_unit(self, request):
        data = request.data

        profile_validate = ListEmailByUnitValidate(data=data)
        if not profile_validate.is_valid():
            return response_data(status=4,
                                 message=list(profile_validate.errors.values())[0][0])
        try:
            unit = data.get("unit")
            unit_name = data.get("unit_name")
            department = Department.objects
            if unit == "branch":
                if unit_name == "ALL":
                    department = department.exclude(Q(branch=None) | Q(branch="")).all()
                elif unit_name == "TINPNC":
                    department = department.filter(Q(branch="TIN") | Q(branch="PNC")).all()
                elif unit_name == "TIN":
                    department = department.filter(branch=unit_name).all()
                elif unit_name == "PNC":
                    department = department.filter(branch=unit_name).all()
                else:
                    return response_data(status=5, message="branch không hợp lệ!")
            elif unit == "parent_depart":
                department = department.filter(parent_depart=unit_name).all()
            elif unit == "agency":
                department = department.filter(chi_nhanh=unit_name).all()
            else:
                department = department.filter(child_depart=unit_name).all()

            child_depart_list = department.values_list('child_depart')
            child_depart_list = [x[0] for x in child_depart_list]
            employee_data = Employee.objects.filter(child_depart__in=child_depart_list, status_working=1)
            employee_serializer = EmployeeSerializer(employee_data, many=True, fields=["email"])

            email_list = [x["email"] for x in employee_serializer.data]

            return response_data(data=email_list)
        except Exception as ex:
            print(f"[{datetime.now()}][get_list_email_by_unit] >> {ex}")
            return response_data(status=4, message=f"Lỗi hệ thống: {ex}")

    def get_all_profile(self, request):
        user_token = authSessionHandler.get_user_token(request)
        try:
            user_id = user_token.get("userId")
            if user_token and user_token.get("email", None) is not None:
                email = user_token.get("email")
            else:
                raise ValueError("Token expired")
        except Exception as ex:
            print(ex)
            return response_data(status=3, message="Token expired")
        # try:
        #     data_redis = user_token
        #     name = data_redis["fullName"]
        # except:
        #     name = "---"
        # try:
        #     token_hr = hr_auth()
        #     dataApi = get_employee_info(token=token_hr, email=email)
        # except:
        #     dataApi = {}
        try:
            code = user_token.pop("employeeCode", "---")
            safe_card_query = SafeCard.objects.filter(emp_code=code)
            safe_card_data = SafeCardSerializer(safe_card_query, many=True).data
        except:
            safe_card_data = {}
        try:
            safe_card_data = safe_card_data[0]
        except:
            safe_card_data = {}
        picture_certificate = safe_card_data.pop("pictureCertificate", "---")
        if picture_certificate != "---" and picture_certificate is not None:
            picture_certificate = SAFE_CARD_LINK["host"] + picture_certificate
        elif picture_certificate is None:
            picture_certificate = "---"
        date_certificate = safe_card_data.pop("dateCertificate", "---")
        expiration_date = safe_card_data.pop("expirationDate", "---")
        try:
            dateEnd = datetime.strptime(expiration_date, '%Y-%m-%d')
            dateStart = datetime.strptime(date_certificate, '%Y-%m-%d')
            month_safe_card = rd(dateEnd, dateStart).months + 1
            month_safe_card = str(month_safe_card) + " tháng"
            date_certificate = self.date_format(dateStart)
            expiration_date = self.date_format(dateEnd)
        except:
            month_safe_card = date_certificate = expiration_date = "---"
        try:
            pk = self.get_emp_code(email)
            if pk:
                pk = pk.get("emp_code", None)

            data = {}
            if pk:
                data = self.get_employee(pk)
            else:
                pass
                # if not is_empty(email):
                #     fields = ["avatarImg"]
                #     user_profile_data = self.get_user_profile_with_email(email=email, fields=fields)
                #     data['avatarImg'] = user_profile_data["avatarImg"]

            avatarImg = MyInfoUserProfileSerializer.get_avarta_from_user_id(user_id)
            if avatarImg is None or avatarImg == "":
                gender_user = data.get("sex", 'M')
                if gender_user == "M":
                    avatarImg = AVATAR_DEFAULT["male"]
                else:
                    avatarImg = AVATAR_DEFAULT["female"]

            # print("data: ", data)
            # if data['avatarImg'] is not None and data['avatarImg'] != "" \
            #         and data['avatarImg'].startswith(("http://", "https://")):
            #     avatarImg = data['avatarImg']
            # elif data["sex"] == "M":
            #     avatarImg = AVATAR_DEFAULT["male"]
            # else:
            #     avatarImg = AVATAR_DEFAULT["female"]
        except:
            data = {}
            avatarImg = AVATAR_DEFAULT["male"]

        # try:
        #     if data["name"] is not None and data['name'] != "":
        #         dataApi["fullName"] = data["name"]
        #         # print(data)
        # except:
        #     dataApi["fullName"] = name
        name = user_token.get('name')

        # if data["empCode"] is not None and data['empCode'] != "":
        #     code = data.get("empCode", "------")
        code = data.get("code", "------")
        # else:
        #     code = "------"

        try:
            start_working_time = data.pop("dateJoinCompany", "---")
            work_time_data = datetime.strptime(start_working_time, '%d/%m/%Y')
            working_day = str(rd(datetime.now(), work_time_data).days)
        except:
            start_working_time = "---"
            working_day = "---"
        data_output = {
            "profile": {
                "email": email,
                "code": code,
                "name": name,
                "birthday": data.pop("birthday", "---"),
                "jobTitle": data.pop("jobTitle", "---"),
                "childDepart": data.pop("childDepart", "---"),
                "mobilePhone": data.pop("mobilePhone", "---"),
                "avatarImg": avatarImg,
                "locationJob": "---",
                "familyCircumstances": "---",
                "salary": "--- vnd"  # dataApi.pop("employeeCode", "---"),
            },
            "occupationalSafetyCard": {
                "month": month_safe_card,
                "dayStart": date_certificate,
                "dayEnd": expiration_date,
                "pictureCertificate": picture_certificate
            },
            "timeJob": {
                "dateJoinCompany": start_working_time,
                "totalDay": working_day
            },
            "contract": {
                "contractType": data.pop("contractType", "---"),
                "contractBegin": data.pop("contractBegin", "---"),
                "contractEnd": data.pop("contractEnd", "---")
            }
        }
        return response_data(data_output)

    def get_profile_overview(self, request):
        self.check_user_info_my_profile(request)

        try:
            emp_code = self.userInfo.get("empCode", None)
            email = self.userInfo.get("email", '')

            profile_data = {}
            is_show_occupational_safety_card = False
            is_show_salary = False
            perm_xem_luong = self.userInfo["permissions"].get("XEM_LUONG", None)
            # print("EMP_CODE: ", emp_code)
            if not is_empty(emp_code):
                fields = ["name", "jobTitle", "totalDay", "avatarImg", "gender"]
                employee_data = self.get_employee_info_with_emp_code(emp_code, fields=fields)
                # cap nhat data
                if employee_data:
                    profile_data.update(employee_data)

                # lay thong tin ma phong ban de lay branch cua nhan vien
                child_depart = self.userInfo.get("childDepart", None)
                if child_depart:
                    department = Department.objects.filter(child_depart=child_depart).first()
                    profile_data["branch"] = department.branch if department else "---"

                # nhan vien duoc quyen show bac nghe
                if self.check_show_data_employee(employee_data["jobTitle"], "is_show_job_level"):
                    job_level = self.getEmployeeLevel(emp_code=emp_code)
                    profile_data["jobLevel"] = str(job_level) if job_level else "---"

                # nhan vien duoc quyen show the an toan lao dong
                if self.check_show_data_employee(employee_data["jobTitle"], "is_show_occupational_safety_card"):
                    is_show_occupational_safety_card = True

                # nhan vien duoc quyen show luong
                if self.check_show_data_employee(employee_data["jobTitle"], "is_show_salary") or perm_xem_luong:
                    is_show_salary = True
            else:
                # email = self.userInfo.get("email", None)

                if not is_empty(email):
                    fields = ["name", "avatarImg"]
                    user_profile_data = self.get_user_profile_with_email(email=email, fields=fields)
                    # cap nhat data
                    profile_data.update(user_profile_data)

            # xu ly anh dai dien
            try:
                gender = profile_data.pop("gender", None)
                user_id = profile_data.get("userId", '')
                avatar = MyInfoUserProfileSerializer.get_avatar_from_email(email)
                # avatar = MyInfoUserProfileSerializer.get_avarta_from_user_id(user_id)

                if avatar == "":
                    avatar = AVATAR_DEFAULT['male']
                    if gender == "F":
                        avatar = AVATAR_DEFAULT['female']
                profile_data["avatarImg"] = avatar

                # avatar = profile_data["avatarImg"]

                # if avatar and avatar != "" and avatar != "---" \
                #         and avatar.startswith(("http://", "https://")):
                #     profile_data["avatarImg"] = avatar
                # elif (avatar == "" or avatar == "---") and gender == "M":
                #     profile_data["avatarImg"] = AVATAR_DEFAULT["male"]
                # elif (avatar == "" or avatar == "---") and gender == "F":
                #     profile_data["avatarImg"] = AVATAR_DEFAULT["female"]
                # else:
                #     raise Exception("Không có avatar và không phân biệt được giới tính.")
            except:
                profile_data["avatarImg"] = AVATAR_DEFAULT["male"]

            data = {
                "avatar": profile_data.pop("avatarImg", "---"),
                "name": profile_data.pop("name", "--"),
                "jobTitle": profile_data.pop("jobTitle", "---"),
                "branch": profile_data.pop("branch", "---"),
                "totalDay": profile_data.pop("totalDay", "---"),
                "jobLevel": profile_data.pop("jobLevel", ""),
                "isShowOccupationalSafetyCard": is_show_occupational_safety_card,
                "isShowSalary": is_show_salary
            }
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_profile_overview >> {ex}")
            return response_data(status=4, message="Lỗi server!")

    def get_profile_detail(self, request):
        self.check_user_info_my_profile(request)

        try:
            emp_code = self.userInfo.get("empCode", None)

            profile_data = {}
            if not is_empty(emp_code):
                fields = ["gender", "birthday", "placeOfBirth",
                          "nationality", "identityCardNo", "date", "issuedAt",
                          "placeOfPermanent", "maritalStatus", "degree",
                          "mobilePhone", "email"]
                employee_data = self.get_employee_info_with_emp_code(emp_code, fields=fields)
                profile_data.update(employee_data)
            else:
                email = self.userInfo.get("email", None)
                if not is_empty(email):
                    fields = ["email", "birthday"]
                    user_profile_data = self.get_user_profile_with_email(email=email, fields=fields)
                    profile_data.update(user_profile_data)

            data = {
                "gender": profile_data.pop("gender", "---"),
                "birthday": profile_data.pop("birthday", "---"),
                "placeOfBirth": profile_data.pop("placeOfBirth", "---"),
                "nationality": profile_data.pop("nationality", "---"),
                "identityCardNo": profile_data.pop("identityCardNo", "---"),
                "date": profile_data.pop("date", "---"),
                "issuedAt": profile_data.pop("issuedAt", "---"),
                "placeOfPermanent": profile_data.pop("placeOfPermanent", "---"),
                "maritalStatus": profile_data.pop("maritalStatus", "---"),
                "degree": profile_data.pop("degree", "---"),
                "mobilePhone": profile_data.pop("mobilePhone", "---"),
                "email": profile_data.pop("email", "---")
            }
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_profile_detail >> {ex}")
            return response_data(status=4, message="Lỗi server!")

    def get_working_information(self, request):
        self.check_user_info_my_profile(request)

        try:
            emp_code = self.userInfo.get("empCode", None)

            working_info_data = {}
            workplace = {
                "workplaceName": "---",
                "workplaceLat": "",
                "workplaceLng": ""
            }
            block = {
                "isShowBlock": False,
                "blockName": "",
                "blockLat": "",
                "blockLng": ""
            }

            if not is_empty(emp_code):
                fields = ["code", "dateJoinCompany", "level", "childDepart", "workplace", "jobTitle"]
                employee_data = self.get_employee_info_with_emp_code(emp_code, fields=fields)
                if employee_data:
                    workplace["workplaceName"] = employee_data.pop("workplace", "---")
                    working_info_data.update(employee_data)

                data_api = self.get_info_checkin_from_emp_code(emp_code)
                block_name = None
                coordinate_block = None
                if data_api and data_api["statusCode"] == 1:
                    block_name = data_api['data'].pop("blockName", None)
                    coordinate_block = data_api['data'].pop("coordinateBlock", None)
                    coordinate_office = data_api['data'].pop("coordinateOffice", None)

                    # tach toa do van phong
                    if not is_empty(coordinate_office):
                        lat, lng = coordinate_office.split(',')
                        workplace.update({
                            "workplaceLat": lat,
                            "workplaceLng": lng
                        })

                # nhan vien duoc quyen show block
                if self.check_show_data_employee(employee_data["jobTitle"], "is_show_block"):
                    block.update({
                        "isShowBlock": True,
                        "blockName": block_name if block_name and block_name != "" else "---",
                    })
                    if not is_empty(coordinate_block):
                        # tach toa doa block
                        lat, lng = coordinate_block.split(',')
                        block.update({
                            "blockLat": lat,
                            "blockLng": lng,
                        })

            data = {
                "code": working_info_data.pop("code", "---"),
                "dateJoinCompany": working_info_data.pop("dateJoinCompany", "---"),
                "level": working_info_data.pop("level", "---"),
                "workplace": workplace,
                "isShowBlock": block.pop("isShowBlock", False),
                "blockName": block.pop("blockName", "---"),
                "blockLat": block.pop("blockLat", ""),
                "blockLng": block.pop("blockLng", ""),
                "childDepart": working_info_data.pop("childDepart", "---")
            }
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_working_information >> {ex}")
            return response_data(status=4, message="Lỗi server!")

    def get_salary_account(self, request):
        self.check_user_info_my_profile(request)

        try:
            emp_code = self.userInfo.get("empCode", None)

            salary_data = {}
            if not is_empty(emp_code):
                fields = ["accountNumber", "bankName"]
                employee_data = self.get_employee_info_with_emp_code(emp_code, fields=fields)
                salary_data.update(employee_data)

            data = {
                "accountNumber": salary_data.pop("accountNumber", "---"),
                "bankName": salary_data.pop("bankName", "---"),
            }
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_salary_account >> {ex}")
            return response_data(status=4, message="Lỗi server!")

    def get_insurance_tax(self, request):
        self.check_user_info_my_profile(request)

        try:
            emp_code = self.userInfo.get("empCode", None)

            insurance_tax_data = {}
            if not is_empty(emp_code):
                fields = ["healthInsurance", "socialInsurance",
                          "socialInsuranceSalaryPay", "placeToJoinSocialInsurance",
                          "taxIdentificationNumber", "taxIdentificationPlace",
                          "taxIdentificationDate"]
                employee_data = self.get_employee_info_with_emp_code(emp_code, fields=fields)
                insurance_tax_data.update(employee_data)

            data = {
                "healthInsurance": insurance_tax_data.pop("healthInsurance", "---"),
                "socialInsurance": insurance_tax_data.pop("socialInsurance", "---"),
                "socialInsuranceSalaryPay": insurance_tax_data.pop("socialInsuranceSalaryPay", "---"),
                "placeToJoinSocialInsurance": insurance_tax_data.pop("placeToJoinSocialInsurance", "---"),
                "taxIdentificationNumber": insurance_tax_data.pop("taxIdentificationNumber", "---"),
                "taxIdentificationPlace": insurance_tax_data.pop("taxIdentificationPlace", "---"),
                "taxIdentificationDate": insurance_tax_data.pop("taxIdentificationDate", "---"),
            }
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_insurance_tax >> {ex}")
            return response_data(status=4, message="Lỗi server!")

    def get_contracts(self, request):
        self.check_user_info_my_profile(request)

        try:
            emp_code = self.userInfo.get("empCode", None)

            if not is_empty(emp_code):
                contract_data = Contract.objects.filter(emp_code=emp_code).order_by(
                    F('contract_end_date').desc(nulls_first=True)).all()
                if contract_data.exists():
                    paginator = self.pagination_class
                    try:
                        contract_data = paginator.paginate_queryset(contract_data, request)
                    except:
                        api_save_log(request=request, api_status=0, err_analysis=-1, api_name="get_contracts",
                                     status_code=5, message="page không hợp lệ!")
                        return response_data(status=5, message="page không hợp lệ!")
                    else:
                        contract_serializer = MyInfoContractSerializer(contract_data, many=True)
                        serializer_data = contract_serializer.data

                        data_response = paginator.get_paginated_response(serializer_data)

                        api_save_log(request=request, data_output=data_response.data, api_name="get_contracts")
                        return response_data(data=data_response.data)
                else:
                    contract_list = []
                    employee_data = self.get_employee_info_with_emp_code(emp_code,
                                                                         fields=["contractCode",
                                                                                 "contractType",
                                                                                 "contractStartDate",
                                                                                 "contractEndDate",
                                                                                 "recodedType"])

                    recoded_type = "---"
                    contract_end_date = employee_data.get("contractEndDate", None)
                    if contract_end_date and contract_end_date != "" and contract_end_date != "---":
                        contract_end_date = datetime.strptime(str(contract_end_date), "%d/%m/%Y")
                        now_date = datetime.strptime(str(datetime.now().date()),
                                                     helper.format_date)
                        if contract_end_date < now_date:
                            recoded_type = "EXPIRED"
                        else:
                            recoded_type = "DUE"
                    elif employee_data["contractType"] == "HĐLĐ Không xác định thời hạn":
                        recoded_type = "DUE"

                    contract_list.append({
                        "contractCode": employee_data.pop("contractCode", "---"),
                        "contractType": employee_data.pop("contractType", "---"),
                        "contractStartDate": employee_data.pop("contractStartDate", "---"),
                        "contractEndDate": employee_data.pop("contractEndDate", "---"),
                        "recodedType": recoded_type,
                    })

                    data_response = {
                        "pageNumber": 1,
                        "results": contract_list
                    }
                    api_save_log(request=request, data_output=data_response, api_name="get_contracts")
                    return response_data(data=data_response)
            else:
                api_save_log(request=request, api_status=0, err_analysis=0, api_name="get_contracts", status_code=4,
                             message="Không có thông tin hợp đồng!")
                return response_data(status=4, message="Không có thông tin hợp đồng!")
        except Exception as ex:
            print(f"{datetime.now()} >> get_insurance_tax >> {ex}")
            api_save_log(request=request, api_status=0, err_analysis=0, api_name="get_contracts", status_code=4,
                         message="Lỗi server!")
            return response_data(status=4, message="Lỗi server!")

    def occupational_safety_card_by_emp_code(self, request):
        self.check_user_info_my_profile(request)

        try:
            updated_verifier = self.update_situation_safe_card()

            if 1 != updated_verifier.data["statusCode"]:
                return updated_verifier

            employee_code = self.userInfo.get("empCode", "")
            employee_data = Employee.objects.filter(emp_code=employee_code).first()
            if employee_data is None:
                return response_data(status=4, message="Mã nhân viên không tồn tại!")

            if employee_data.job_title not in [emp_position for emp_position in EMPLOYEE_POSITION]:
                return response_data(status=4, message="Đây không phải là NVKT/OS, INDO, TF!")

            paginator = self.pagination_class

            safe_card_query = SafeCard.objects \
                .filter(emp_code=employee_code).exclude(tinh_trang_the_chung_chi="Chưa Cấp") \
                .order_by(F('ngay_het_han_ATLD').desc(nulls_first=True)).all()
            try:
                safe_card_data = paginator.paginate_queryset(safe_card_query, request)
            except:
                return response_data(status=5, message="page không hợp lệ!")
            else:
                serializer = MyInfoSafeCardSerializer(safe_card_data, many=True,
                                                      context={"request": request})

                data_response = paginator.get_paginated_response(serializer.data)
                return response_data(data=data_response.data)
        except Exception as ex:
            print(f"{datetime.now()} >> occupational_safety_card_by_emp_code >> {ex}")
            return response_data(status=4, message="Lỗi server!")

    def get_application_info(self, request):
        data = {
            "latestVer": "---",
            "menu": [],
            "currentVersionLabel": "---",
            "newVersionLabel": "---"
        }
        config_key = global_data.LATEST_APP_VERSION_INFO
        try:
            config_setting_res = self.get_setting_config_by_key(config_key)
            if config_setting_res and config_setting_res["statusCode"] == 1:
                config_data = config_setting_res["data"]
                config_value = config_data["config_value"]
                latest_version = config_value["latestVer"]
                app_info_data = config_value["appInfo"]

                data["latestVer"] = latest_version if latest_version else "---"
                data["menu"] = app_info_data["menu"] if app_info_data["menu"] else "---"
                data["currentVersionLabel"] = app_info_data["currentVersionLabel"] \
                    if app_info_data["currentVersionLabel"] else "---"
                data["newVersionLabel"] = app_info_data["newVersionLabel"] if app_info_data[
                    "newVersionLabel"] else "---"
        except Exception as ex:
            print(f"{datetime.now()} >> get_application_info >> {ex}")
            api_save_log(request=request, data_output=str(ex), api_status=0, err_analysis=0,
                         api_name="get_application_info", message="Thất bại")
            return response_data(data=str(ex), message="Thất bại", status=1)

        api_save_log(request=request, data_output=data, api_name="get_application_info")
        return response_data(data=data)

    def get_device_info(self, request):
        self.check_user_info_my_profile(request)

        device_info = {
            "deviceId": "---",
            "deviceName": "---",
            "status": "---"
        }

        try:
            employee_code = self.userInfo.get("empCode", None)
            email = self.userInfo.get("email", None)
            device_id_login = self.userInfo.get("deviceId", "")
        except Exception as ex:
            print(f"{datetime.now()} >> lay thong tin email, emp code >> {ex}")
            api_save_log(request=request, api_status=0, err_analysis=0, api_name="get_device_info", status_code=4,
                         message=str(ex))
            return response_data(status=4, message="Lỗi server!")

        try:
            # lay thong tin ten thiet bi
            if not is_empty(email):
                data_api = self.get_user_devices_info_by_email(email)
                if data_api and data_api["statusCode"] == 1:
                    device_info_api = data_api["data"]
                    device_info["deviceName"] = device_info_api["deviceName"] if not is_empty(
                        device_info_api["deviceName"]) else "---"
        except Exception as ex:
            print(f"{datetime.now()} >> lay thong tin thiet bi gap loi >> {ex}")

        try:
            # goi sang service mypt-checkin-api de lay deviceId, blockName, coordinateBlock, coordinateOffice
            data_api = self.get_info_checkin_from_emp_code(employee_code)

            if data_api and data_api["statusCode"] == 1:
                device_id = data_api['data'].pop("deviceId", None)
                device_info["deviceId"] = device_id if device_id and device_id != "" else "---"
                if device_id:
                    if device_id == device_id_login:
                        device_info["status"] = "Đã đăng ký"
                    else:
                        device_info["status"] = "Chưa đăng ký"
                else:
                    device_info["status"] = "---"
        except Exception as ex:
            print(f"{datetime.now()} >> lay thong tin deviceId, blockName, coordinateBlock, coordinateOffice >> {ex}")

        try:
            config_key = "DEVICE_INFO"
            config_setting_res = self.get_setting_config_by_key(config_key)
            if config_setting_res and config_setting_res["statusCode"] == 1:
                config_data = config_setting_res["data"]
                config_value = config_data["config_value"]
                device_info_data = config_value["deviceContent"]

                device_info["content"] = device_info_data
        except Exception as ex:
            print(f"{datetime.now()}  >> {ex}")
            device_info["content"] = []
        api_save_log(request=request, data_output=device_info, api_name="get_device_info")
        return response_data(data=device_info)

    def update_avatar(self, request):
        self.check_user_info_my_profile(request)

        avatar_url = request.data.get("avatarUrl", None)
        if avatar_url is None:
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=-1,
                         api_name="update_avatar", status_code=5, message="Thiếu đường dẫn")
            return response_data(status=5, message="Thiếu đường dẫn")
        if avatar_url is None or avatar_url == "":
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=-1,
                         api_name="update_avatar", status_code=5, message="Dường dẫn rỗng!")
            return response_data(status=5, message="Dường dẫn rỗng!")

        if not avatar_url.startswith(("https://apis.fpt.vn/", "https://apis-stag.fpt.vn/",
                                      "http://apis.fpt.vn/", "http://apis-stag.fpt.vn/")):
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=-1,
                         api_name="update_avatar", status_code=5, message="Đường dẫn không hợp lệ!")
            return response_data(status=5, message="Đường dẫn không hợp lệ!")
        try:
            proxies = {
                "http": "http://proxy.hcm.fpt.vn:80",
                "https": "http://proxy.hcm.fpt.vn:80"
            }
            image_response = requests.head(avatar_url, timeout=5, proxies=proxies)
        except Exception as ex:
            print(f"{datetime.now()} >> kiem tra link hinh anh co loi >> {ex}")
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=0, api_name="update_avatar",
                         status_code=4, message="Thay đổi ảnh đại diện không thành công!")
            return response_data(status=4, message="Thay đổi ảnh đại diện không thành công!")

        if image_response.status_code != 200:
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=-1,
                         api_name="update_avatar", status_code=5, message="Đường dẫn không hợp lệ!")
            return response_data(status=5, message="Đường dẫn không hợp lệ!")

        images_headers = image_response.headers
        if images_headers["Content-Type"] not in ['image/heic', 'image/png', 'image/jpeg']:
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=-1,
                         api_name="update_avatar", status_code=5, message="Loại file không hợp lệ!")
            return response_data(status=5, message="Loại file không hợp lệ!")

        email = self.userInfo.get("email", None)
        employee_code = self.userInfo.get("empCode", None)

        employee_data = Employee.objects.filter(email=email).first()
        user_profile_data = UserProfile.objects.filter(email=email).first()

        try:
            if employee_data and employee_data.emp_code == employee_code:
                employee_data.avatar_img = avatar_url
                employee_data.save()

            if user_profile_data:
                user_profile_data.avatar_img = avatar_url
                user_profile_data.save()
            # print(request.headers)
        except Exception as ex:
            print(f"{datetime.now()} >> update_avatar >> {ex}")
            api_save_log(request=request, data_input=avatar_url, api_status=0, err_analysis=0, api_name="update_avatar",
                         status_code=4, message="Thay đổi ảnh đại diện không thành công!")
            return response_data(status=4, message="Thay đổi ảnh đại diện không thành công!")
        else:
            api_save_log(request=request, data_input=avatar_url, api_name="update_avatar",
                         message="Thay đổi ảnh đại diện thành công")
            return response_data(status=1, message="Thay đổi ảnh đại diện thành công")

    # API private cap nhat birthday cho table user_profile
    def update_birthday_profile(self, request):
        try:
            employee_data = Employee.objects.all()
            serializer = EmployeeSerializer(employee_data, many=True, fields=["email", "birthday"])

            for employee_serializer in serializer.data:
                if employee_serializer["birthday"] is not None:
                    _birthday = datetime.strptime(employee_serializer["birthday"], "%d/%m/%Y")
                    str_birthday = datetime.strftime(_birthday, "%Y-%m-%d")
                    UserProfile.objects.filter(email=employee_serializer["email"]).update(
                        birthday=str_birthday)
            return response_data(status=1, message="Cập nhật thông tin ngày sinh tất cả profile thành công.")
        except Exception as ex:
            print(f"{datetime.now()} >> update_birthday_profile >> {ex}")
            return response_data(status=4, message="Cập nhật thông tin ngày sinh tất cả profile không thành công!")

    # cac api private de service mypt-job-api goi dong bo luong
    def get_all_employee_empty_salary_daily(self, request):
        try:
            data = request.data

            status_working = data.get("statusWorking", 1)
            job_title = data.get("jobTitle", ['CB Kỹ thuật TKBT', 'cb kỹ thuật tkbt'])
            first_time_of_date = data.get("firstTimeOfDate", None)
            if first_time_of_date is None:
                raise ValueError("first_time_of_date la null!")

            employees = Employee.objects.filter(
                Q(status_working=status_working)
                & Q(job_title__in=job_title)
                & (Q(salary_daily_date_last_sync=None) | Q(salary_daily_date_last_sync__lt=first_time_of_date))) \
                .values('emp_code', 'email', 'salary_daily_date_last_sync')

            return response_data(data=employees)
        except Exception as ex:
            print(f"{datetime.now()} >> get_all_employee_empty_salary_daily >> {ex}")
            return response_data(status=4, data=[])

    def get_all_employee_empty_salary_monthly(self, request):
        try:
            data = request.data

            status_working = data.get("statusWorking", 1)
            job_title = data.get("jobTitle", ['CB Kỹ thuật TKBT', 'cb kỹ thuật tkbt'])
            first_time_of_date = data.get("firstTimeOfDate", None)
            if first_time_of_date is None:
                raise ValueError("first_time_of_date la null!")

            employees = Employee.objects \
                .filter(Q(status_working=status_working)
                        & Q(job_title__in=job_title)
                        & (Q(salary_monthly_date_last_sync=None)
                           | Q(salary_monthly_date_last_sync__lt=first_time_of_date))) \
                .values('emp_code', 'email', 'salary_monthly_date_last_sync')

            return response_data(data=employees)
        except Exception as ex:
            print(f"{datetime.now()} >> get_all_employee_empty_salary_monthly >> {ex}")
            return response_data(status=4, data=[])

    def update_employee_salary_day_sync_status(self, request):
        try:
            data = request.data
            employees = data.get("employees", {})
            with transaction.atomic():
                for key, value in employees.items():
                    Employee.objects.filter(emp_code=key) \
                        .update(salary_daily_date_last_sync=value)
            return response_data()
        except Exception as ex:
            print(f"{datetime.now()} >> update_employee_salary_day_sync_status >> {ex}")
            return response_data(status=4, message=ex)

    def update_employee_salary_month_sync_status(self, request):
        try:
            data = request.data
            employees = data.get("employees", {})
            with transaction.atomic():
                for key, value in employees.items():
                    Employee.objects.filter(emp_code=key) \
                        .update(salary_monthly_date_last_sync=value)
            return response_data()
        except Exception as ex:
            print(f"{datetime.now()} >> update_employee_salary_month_sync_status >> {ex}")
            return response_data(status=4, message=ex)

    def get_list_email_pdx(self, request):
        try:
            data = Employee.objects.filter(child_depart='PCDSDX').values_list('email', flat=True)
            return response_data(data=data)
        except Exception as ex:
            print(f"{datetime.now()} >> get_email_pdx >> {ex}")
            return []

    def get_features_roles_emails_improve_car(self, request):
        data = request.data
        # có email thì check theo email đó có quyền hay không
        role_codes = data.get('role_codes', [])
        if 'email' in data:

            try:
                if FeaturesRolesEmails.objects.filter(
                        email=data['email'], role_code__in=role_codes
                ).exists():
                    return response_data(data=True)

                return response_data(data=False)
            except Exception as ex:
                print(f"{datetime.now()} >> get_features_roles_emails_improve_car permission >> {ex}")
                return response_data(data=False)

        # ngược lại trả danh sách email có quyền
        try:
            data = FeaturesRolesEmails.objects.filter(
                role_code__in=role_codes).values_list('email', flat=True)

            return response_data(data=data)

        except Exception as ex:
            print(f"{datetime.now()} >> get_features_roles_emails_improve_car list email >> {ex}")
            return []

    # API nay chi de goi private, de lay thong tin employee cho danh sach cac email
    def emps_info_by_emails(self, request):
        postData = request.data.copy()
        userEmails = postData.get("emails", [])
        if len(userEmails) <= 0:
            return response_data(status=5, message="Missing email(s)", data=None)

        empQs = Employee.objects.filter(email__in=userEmails)
        emp_ser = EmployeeSerializer(empQs, many=True)
        emps_arr = emp_ser.data
        if len(emps_arr) <= 0:
            return response_data({"emps_info_data": []})

        emps_info_data = []
        emps_child_departs = []
        for emp_row in emps_arr:
            emp_item = {
                "email": emp_row["email"].lower(),
                "emp_code": emp_row["code"],
                "full_name": emp_row["name"],
                "job_title": emp_row["jobTitle"],
                "branch": "",
                "parent_depart": "",
                "agency": "",
                "child_depart": emp_row["childDepart"]
            }
            emps_info_data.append(emp_item)
            emps_child_departs.append(emp_row["childDepart"])

        # Lay agency, parent_depart, branch cua tung employee
        if len(emps_child_departs) > 0:
            departQs = Department.objects.filter(child_depart__in=emps_child_departs)
            departs_ser = DepartmentSerializer(departQs, many=True)
            departs_arr = departs_ser.data
            if len(departs_arr) > 0:
                for empItem in emps_info_data:
                    childDepStr = empItem["child_depart"]
                    for childDepart_item in departs_arr:
                        if childDepart_item["childDepart"] == childDepStr:
                            empItem["agency"] = childDepart_item["agency"]
                            empItem["parent_depart"] = childDepart_item["parentDepart"]
                            empItem["branch"] = childDepart_item["branch"]
                            break

        return response_data({"emps_info_data": emps_info_data})

    # api này dung de lay link avatar voi input la 1 email (api goi private)

    def get_list_avatar_from_list_email(self, request):
        data_input = request.data
        list_email = data_input.get("list_email", None)
        if not isinstance(list_email, list):
            return response_data(data={}, message='Input danh sách email không đúng', status=0)
        list_email = [str(email).lower() for email in list_email]
        link_avatar = AVATAR_DEFAULT['male']

        data_resp = {
            email: link_avatar for email in list_email
        }
        try:
            list_email_female = Employee.objects.filter(email__in=list_email, sex='F').values_list('email', flat=True)

            data_resp.update({
                email.lower(): AVATAR_DEFAULT['female'] for email in list_email_female
            })

            profile_info = UserProfile.objects.filter(email__in=list_email).values('email', 'avatar_img')

            for i in profile_info:
                if i['avatar_img']:
                    data_resp.update({i['email'].lower(): i['avatar_img']})
            return response_data(data=data_resp)
        except Exception as ex:
            print("api_get_avatar_from_email >> Error/loi: {}".format(ex))
            return response_data(data=data_resp, message=MESSAGE_API_SUCCESS, status=0)

    # api dung de lay data ve phong ban tu 1 list email:
    def api_info_child_depart_for_list_email(self, request):
        fname = "api_info_child_depart_for_email"
        data_input = request.data
        list_email = data_input.get("list_email", [])
        try:
            if len(list_email) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_INPUT, status=STATUS_CODE_INVALID_INPUT)

            email_join = "\",\"".join(list_email)
            query = "SELECT a.emp_code, a.email, a.job_title, a.child_depart, b.chi_nhanh, b.parent_depart, b.branch, c.province_code," \
                    " d.province_name, d.region_code  FROM employees_tb a " \
                    "INNER JOIN department_tb b ON a.child_depart = b.child_depart " \
                    "INNER JOIN mypt_profile_agency_and_province c ON b.chi_nhanh = c.agency " \
                    "LEFT JOIN mypt_profile_provinces_and_regions d ON c.province_code = d.province_code  " \
                    "WHERE a.email IN  (\"{}\")".format(email_join)

            cursor = connection.cursor()
            cursor.execute(query)
            data_row = cursor.fetchall()

            if len(data_row) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            data_output = {}

            for i in data_row:
                emp_code = i[0]
                email = i[1].lower()
                job_title = i[2]
                child_depart = i[3]
                agency = i[4]
                parent_depart = i[5]
                branch = i[6]
                province_code = i[7]
                province_name = i[8]
                region_code = i[9]

                if province_name is None:
                    province_name = ""
                if region_code is None:
                    region_code = ""

                data_output.update({
                    email: {
                        "emp_code": emp_code,
                        'job_title': job_title,
                        'child_depart': child_depart,
                        'agency': agency,
                        'parent_depart': parent_depart,
                        'branch': branch,
                        'province_code': province_code,
                        'province_name': province_name,
                        'region_code': region_code
                    }
                })

            return response_data(data=data_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("api_info_child_depart_for_email >> Error/loi: {}".format(ex))
            return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

    # api dung de save thong tin vung vao redis

    def api_save_redis_region(self, request):
        try:
            queryset = ProvincesAndRegion.objects.all().values('province_name', 'province_code', 'region',
                                                               'region_code')
            if len(queryset) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            # "region_code": {
            #     "name": "region name",
            #     "provinces": {
            #         "province_code": "province_name"
            #     }
            # }

            dict_data_province = {}
            dict_data_output = {}

            for i in queryset:
                region_code = i['region_code']
                region = i['region']
                province_name = i['province_name']
                province_code = i['province_code']

                # dict_data_province.update({
                #     province_code: province_name
                # })

                data_region = dict_data_output.get(region_code, {})
                if len(data_region) == 0:
                    dict_data_output.update({
                        region_code: {
                            "name": region,
                            "provinces": {
                                province_code: province_name
                            }
                        }
                    })
                else:
                    data_province = data_region.get("provinces", {})
                    data_province.update({
                        province_code: province_name
                    })
                    data_region.update({
                        "provinces": data_province
                    })

                    dict_data_output.update({
                        region_code: data_region
                    })

            dict_data_output = {k: v for k, v in sorted(dict_data_output.items())}
            redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=3,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")

            res_save_redis = redis_instance.set("info_region", json.dumps(dict_data_output))

            #     dict_data_output =  {
            # "VUNG_7": {
            #     "name": "Vùng 7",
            #     "provinces": {
            #         "AN_GIANG": "An Giang",
            #         "BAC_LIEU": "Bạc Liêu",
            #         "BEN_TRE": "Bến Tre",
            #         "CAN_THO": "Cần Thơ",
            #         "CA_MAU": "Cà Mau",
            #         "DONG_THAP": "Đồng Tháp",
            #         "HAU_GIANG": "Hậu Giang",
            #         "KIEN_GIANG": "Kiên Giang",
            #         "LONG_AN": "Long An",
            #         "SOC_TRANG": "Sóc Trăng",
            #         "TIEN_GIANG": "Tiền Giang",
            #         "TRA_VINH": "Trà Vinh",
            #         "VINH_LONG": "Vĩnh Long"
            #     }
            # }}

            return response_data(data=dict_data_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            return response_data(data=str(ex), message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    def process_agency_regions(self, request, *args, **kwargs):
        try:
            queryset_agency = AgencyAndProvince.objects.all()
            serializer_agency = AgencyAndProvinceSerializer(queryset_agency, many=True)

            queryset_depart = Department.objects.all().values('child_depart', 'parent_depart', 'branch', 'chi_nhanh')
            serializer_depart = DepartmentsSerializer(queryset_depart, many=True)

            queryset_emp = Employee.objects.filter(status_working=1)
            serializer_emp = EmployeeSerializer(queryset_emp, many=True).data
            members_by_child_depart = {}
            for emp in serializer_emp.copy():
                child_depart = emp['childDepart']
                if child_depart not in members_by_child_depart:
                    members_by_child_depart[child_depart] = []
                members_by_child_depart[child_depart].append(emp['email'])

            info_depart = {}
            for item in serializer_depart.data.copy():
                child_depart = item['childDepart']
                if item['agency'] not in info_depart:
                    info_depart[item['agency']] = item
                if child_depart in members_by_child_depart:
                    info_depart[item['agency']]['countEmp'] = len(members_by_child_depart[child_depart])
                else:
                    info_depart[item['agency']]['countEmp'] = 0

            data_output = {
                # 'info_users': {},
                # 'info_agency_province': info_agency
            }
        except Exception as ex:
            return response_data(data=str(ex), message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)
        return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
