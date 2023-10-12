from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from project.throttling import UserThrottle
from ...core.helpers import auth_session_handler as authSessionHandler
from ...http.paginations.custom_pagination import *
from ..serializers.improved_car_serializer import *
from ..validations.improved_car_validate import *
from ...core.helpers.response import *
from rest_framework.viewsets import ViewSet
from ...core.helpers.utils_call_api import *
from ..threading.handle_mail import *
from ..threading.handle_notification import *
from django.conf import settings as project_settings
import threading


class ImprovedCarView(ViewSet):
    throttle_classes = []

    def get_throttles(self):
        return [UserThrottle()]

    @staticmethod
    def sum_number_rate(id_tree):
        data = {
            "rate5": "",
            "rate4": "",
            "rate3": "",
            "rate2": "",
            "rate1": ""
        }
        try:
            queryset = RateTheArticle.objects.filter(deleted_at__isnull=True, id_tree=id_tree)
            for i in range(1, 6):
                data['rate' + str(i)] = queryset.filter(rate=i).count()
            return data
        except:
            return data

    @staticmethod
    def get_list_avatar_from_list_email(list_email):
        try:
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            profiles = call_api(
                host=SERVICE_CONFIG['profile_api'][app_env],
                func=SERVICE_CONFIG['profile_api']['get_list_avatar_from_list_email']['func'],
                method=SERVICE_CONFIG['profile_api']['get_list_avatar_from_list_email']['method'],
                data={"list_email": list_email}
            )
            profiles = json.loads(profiles)
            if profiles["statusCode"] != 1:
                profiles = {}
            return profiles['data']
        except Exception as ex:
            print(f'Loi lay danh sach avatar xe cai tien mypt-profile-api: {ex}')
            return {}

    @extend_schema(
        operation_id='Lấy danh sách đánh giá bài viết',
        summary='Lấy danh sách đánh giá bài viết',
        tags=["1. Xe cải tiến"],
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Cảm bạn đã chia sẻ",
                    "data": 3240
                }
            )
        }
    )
    def get_list_rate(self, request):
        data = request.GET
        try:
            validate = PostRateValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)
            queryset = RateTheArticle.objects.filter(deleted_at__isnull=True, id_tree=data["idTree"], rate=data["rate"])
            sum_rate = self.sum_number_rate(id_tree=data['idTree'])
            serializer = RateTheArticleSerializer(queryset, many=True, not_fields=["deletedAt", "updatedAt"])

            dataRate = serializer.data

            list_email = [r['email'] for r in dataRate]

            profiles = self.get_list_avatar_from_list_email(list_email=list_email)

            for r in dataRate:
                if r['email'].lower() in profiles:
                    r['profile'] = {
                        "email": r['email'],
                        "avatarImg": profiles[r['email']]
                    }
            data = {
                "sumRate": sum_rate,
                "dataRate": dataRate
            }
            return response_data(data)
        except:
            return response_data(status=4, message="Lỗi database",
                                 data="Table does not exist or connection fails or input wrong")

    def filter_data_save(self, data_save):
        try:
            data = {}
            for item in data_save:
                if data_save[item] != "":
                    data[item] = data_save[item]
            print(data)
            return data
        except:
            return data_save

    @extend_schema(
        operation_id='Đánh giá bài viết',
        summary='Đánh giá bài viết',
        tags=["1. Xe cải tiến"],
        responses={
            status.HTTP_200_OK: None,
        }
    )
    def post_rate(self, request):
        data = request.data.copy()
        data_input = dict(data)
        email = get_data_from_token(request)
        if email is None:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="post_rate", status_code=5, message=ERROR['TOKEN_NO_INFO']))
            thread.start()
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])

        validate = PostRateValidate(data=data)
        if not validate.is_valid():
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="post_rate", status_code=5, message=list(validate.errors.values())[0][0]))
            thread.start()
            return response_data(status=5, message=list(validate.errors.values())[0][0])

        app_env = "base_http_" + project_settings.APP_ENVIRONMENT

        try:
            email_have_permission = call_api(
                host=SERVICE_CONFIG['profile_api'][app_env],
                func=SERVICE_CONFIG['profile_api']['get_features_roles_emails_improve_car']['func'],
                method=SERVICE_CONFIG['profile_api']['get_features_roles_emails_improve_car']['method'],
                data={
                    "email": email['email'],
                    "role_codes": [ROLE_CODE_NHAN_VIEN_DANH_GIA, ROLE_CODE_NHAN_VIEN_DANH_GIA_PNC,
                                   ROLE_CODE_NHAN_VIEN_DANH_GIA_TIN]
                }
            )
            email_have_permission = json.loads(email_have_permission)
            email_have_permission = email_have_permission['data']
        except Exception as ex:
            print(ex)
            email_have_permission = False

        if not email_have_permission:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="post_rate", status_code=4, message=ERROR['NO_RIGHT_RATE']))
            thread.start()
            return response_data(status=4, message=ERROR['NO_RIGHT_RATE'])

        if RateTheArticle.objects.filter(id_tree=data['idTree'], email=email['email']).exists():
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="post_rate", status_code=4, message=ERROR['RATE_EXISTS']))
            thread.start()
            return response_data(status=4, message=ERROR['RATE_EXISTS'])
        data = self.filter_data_save(data_save=data)
        data["email"] = email["email"]
        dataSave = RateTheArticleSerializer(data=data)
        if dataSave.is_valid():
            dataSave.save()
            queryset = ImprovedCar.objects.filter(id=dataSave.data["idTree"])
            improved_car = ImprovedCarSerializer(queryset, many=True)
            improved_car = improved_car.data[0]
            queryset = ImprovedCarGroup.objects.filter(id=improved_car["typeTitle"]).values("name")
            type_improved_car = queryset[0]["name"].lower()
            subject = project_settings.SUBJECT + " " + type_improved_car
            mail_data = dataSave.data
            mail_data["type_improved_car"] = type_improved_car
            mail_data["improved_car"] = improved_car
            if mail_data["rate"] > 0:
                mail_data["rateLoop"] = [*range(1, mail_data["rate"] + 1)]
            else:
                mail_data["rateLoop"] = []
            mail_data["notRateLoop"] = [*range(mail_data["rate"] + 1, 6)]
            data_notification = {"title": "Đánh giá đề xuất thành công",
                                 "body": "Bạn vừa thực hiện đánh giá đề xuất " + type_improved_car + " thành công",
                                 "topic_type": "idea",
                                 "notifyDataAction": SERVICE_CONFIG["WEBKIT"][project_settings.APP_ENVIRONMENT] + str(
                                     mail_data["id"]), "notifyActionType": "open_webkit", "popupDetailDataAction": "",
                                 "popupDetailActionType": "go_to_screen", "email": mail_data["email"]}
            mail_data[
                "titleContent"] = "My PT cảm ơn Anh/Chị đánh giá về đề xuất " + type_improved_car + " của email " + \
                                  mail_data["improved_car"]["emailCreate"]
            HandleNotification(data=data_notification).start()
            recipient_list = mail_data["email"]
            HandleMail(subject, "reply.html", recipient_list, mail_data, reply=recipient_list).start()
            mail_data[
                "titleContent"] = "Đề xuất " + type_improved_car + " của Anh/Chị vừa nhận được đánh giá từ Anh/Chị " + \
                                  mail_data["email"]
            recipient_list = mail_data["improved_car"]["emailCreate"]
            HandleMail(subject, "reply.html", recipient_list, mail_data, reply=recipient_list).start()
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_name="post_rate", message=SUCCESS['ADD']))
            thread.start()
            return response_data(message=SUCCESS['ADD'])
        thread = threading.Thread(api_save_log(request=request, data_input=data_input, data_output=dataSave.validated_data, api_status=0, err_analysis=0, api_name="post_rate", status_code=4, message=list(dataSave.errors.values())[0][0]))
        thread.start()
        return response_data(message=list(dataSave.errors.values())[0][0], status=4)

    @extend_schema(
        operation_id='Danh sách nhóm bài viết',
        summary='Danh sách nhóm bài viết',
        tags=["1. Xe cải tiến"],
        description='Danh sách nhóm bài viết',
        responses={
            status.HTTP_200_OK: None
        }
    )
    def list_group_improved(self, request):
        data = request.GET
        try:
            queryset = ImprovedCarGroup.objects.filter(deleted_at__isnull=True)
            serializer = ImprovedCarGroupSerializer(queryset, many=True, fields=['id', 'name'])
            return response_data(serializer.data)
        except:
            return response_data(status=4, message="Lỗi database", data="Table does not exist or connection fails")

    def list_like(self, email="", data=None):
        if data is None:
            return data
        try:
            queryset = ImprovedCarLike.objects.filter(email=email, state_like=1)
            serializer = ImprovedCarLikeSerializer(queryset, many=True, fields=['id_tree'])
            data_like = serializer.data
            value = []
            for item in data_like:
                value.append(item["id_tree"])
        except:
            return data
        try:
            for item in data:
                item["isLike"] = item["id"] in value
            return data
        except:
            return data

    def have_rated(self, data, email):
        try:
            for item in data:
                if RateTheArticle.objects.filter(email=email, id_tree=item['id']).exists():
                    item['isRate'] = True
            return data
        except:
            return data

    @extend_schema(
        operation_id='Lấy danh sách bài viết',
        summary='Lấy danh sách bài viết',
        tags=["1. Xe cải tiến"],
        description='Danh sách bài viết',
        responses={
            status.HTTP_200_OK: None
        }
    )
    def get_list_blog(self, request):
        data = request.GET
        data_input = data
        data_redis = get_data_from_token(request)
        email = None
        if data_redis is not None:
            email = data_redis["email"]

        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        try:
            rate = call_api(
                host=SERVICE_CONFIG['profile_api'][app_env],
                func=SERVICE_CONFIG['profile_api']['get_features_roles_emails_improve_car']['func'],
                method=SERVICE_CONFIG['profile_api']['get_features_roles_emails_improve_car']['method'],
                data={
                    "email": email['email'],
                    "role_codes": [ROLE_CODE_NHAN_VIEN_DANH_GIA, ROLE_CODE_NHAN_VIEN_DANH_GIA_PNC,
                                   ROLE_CODE_NHAN_VIEN_DANH_GIA_TIN]
                }
            )
            rate = json.loads(rate)
            rate = rate['data']
        except Exception as ex:
            print(ex)
            rate = False

        if "id" in data:
            queryset = ImprovedCar.objects.filter(id=data["id"], process_status='publish')
            serializer = ImprovedCarSerializer(queryset, many=True, show=True, image=True)

            data = self.list_like(email=email, data=serializer.data)[0]
            data["ruleRate"] = rate
            if RateTheArticle.objects.filter(email=email, id_tree=data['id']).exists():
                data['isRate'] = True

            profiles = self.get_list_avatar_from_list_email(list_email=[data['emailCreate']])
            try:
                profile = {
                    "email": data['emailCreate'],
                    "avatarImg": profiles[str(data['emailCreate']).lower()]
                }
            except Exception as ex:
                profile = {
                    "email": data['emailCreate'],
                    "avatarImg": DEFAULT_AVATAR
                }
                print(f'Error get_list_blog id get_avatar_info: {ex}')

            data["profile"] = profile

            thread = threading.Thread(api_save_log(request=request, data_input=data_input, data_output=data, api_name="get_list_blog_id"))
            thread.start()
            return response_data(data=data)
        if 'sort' in data:
            queryset = ImprovedCar.objects.filter(process_status='publish').order_by("-update_time")
        else:
            queryset = ImprovedCar.objects.filter(process_status='publish')
        paginator = StandardPagination()
        sum = queryset.count()
        per_page = paginator.page_size
        count = sum // per_page
        if sum % per_page > 0:
            count += 1
        result = paginator.paginate_queryset(queryset, request)
        serializer = ImprovedCarSerializer(result, many=True, show=True, image=True)
        blogData = serializer.data
        blogData = self.have_rated(data=blogData, email=email)
        blogData = self.list_like(email=email, data=blogData)
        list_email = [b['emailCreate'] for b in blogData]

        profiles = self.get_list_avatar_from_list_email(list_email=list_email)

        for blog in blogData:
            try:
                if blog['emailCreate'].lower() in profiles:
                    blog['profile'] = {
                        "email": blog['emailCreate'],
                        "avatarImg": profiles[blog['emailCreate'].lower()]
                    }
            except Exception as ex:
                print(f'get_list_blog list get_avatar_info: {ex}')

        data_output = {
            "rate": rate,
            "numberPages": count,
            "list": blogData
        }
        thread = threading.Thread(api_save_log(request=request, data_input=data_input, data_output=data_output, api_name="get_list_blog"))
        thread.start()
        return response_data(data=data_output)

    @extend_schema(
        operation_id='Lấy danh sách bình luận',
        summary='Lấy danh sách bình luận',
        tags=["1. Xe cải tiến"],
        description='Danh sách bình luận',
        responses={
            status.HTTP_200_OK: None,
        }
    )
    def get_list_comment(self, request):
        data_redis = get_data_from_token(request)
        email = None
        if data_redis is not None:
            email = data_redis["email"]
        if 'id' not in request.GET:
            return response_data(status=5, message=ERROR['REQUIRED_ID'])
        id = request.GET['id']
        queryset = ImprovedCarComment.objects.filter(id_tree=id, deleted_at__isnull=True)
        if 'sort' in request.GET:
            queryset = queryset.order_by(request.GET["sort"])
        paginator = StandardPagination()
        count = queryset.count() // paginator.page_size + 1
        serializer = ImprovedCarCommentSerializer(queryset, many=True, show=True)
        commentData = serializer.data

        list_email = [c['email'] for c in commentData]

        profiles = self.get_list_avatar_from_list_email(list_email=list_email)

        try:
            for item in commentData:
                if item['email'].lower() in profiles:
                    item['profile'] = {
                        "email": item['email'],
                        "avatarImg": profiles[item['email'].lower()]
                    }
                if item["email"] == email:
                    item["isDelete"] = True
                else:
                    item["isDelete"] = False
        except Exception as ex:
            print('get_list_comment', ex)

        return response_data(data={
            'numberPages': count,
            'list': commentData
        })

    @extend_schema(
        operation_id='Viết bài viết',
        summary='Viết bài viết',
        tags=["1. Xe cải tiến"],
        description='Viết bài viết',
        request=ImprovedCarValidate,
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Cảm bạn đã chia sẻ",
                    "data": 3240
                }
            )
        }
    )
    def post_blog(self, request):
        data = request.data.copy()
        data_input = data
        user_token = authSessionHandler.get_user_token(request)
        if user_token is None:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="post_blog", status_code=5, message=ERROR['TOKEN_NO_INFO']))
            thread.start()
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        data['emailCreate'] = user_token['email']
        data["branch"] = user_token['branch'] if user_token['branch'] else 'FTEL'

        serializer = ImprovedCarValidate(data=data)
        if not serializer.is_valid():
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="post_blog", status_code=5, message=serializer.errors))
            thread.start()
            return response_data(status=5, message=serializer.errors)
        # up hinh
        # xu ly hinh anh
        # luu tru anh bang cach goi api
        number_file = data.get('numberFile', 0)
        if int(number_file) > 0:
            status_code, msg_code, data_code = call_api_save_file(request, number_file, user_token, "")
            if status_code == 1:
                list_img = data_code.get('linkFile', [])
                str_img = ""
                for item in list_img:
                    if str_img == "":
                        str_img = item
                    else:
                        str_img += ";" + item
                data['imgImprovedCar'] = str_img
                print("---------------------UP HINH THANH CONG--------------------")
                print(list_img)
            else:
                print("---------------------UP HINH --------------------")
                print(msg_code)
                thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="post_blog", status_code=status_code, message="Không thể up hình"))
                thread.start()
                return response_data(data={}, message="Không thể up hình", status=status_code)

        dataSave = ImprovedCarSerializer(data=data)
        if dataSave.is_valid():
            dataSave.validated_data['parent_depart'] = user_token['parentDepart']
            dataSave.validated_data['agency'] = user_token['agency']
            dataSave.save()
            # self.send_email(data=dataSave.data)
            queryset = ImprovedCarGroup.objects.filter(id=dataSave.data["typeTitle"]).values("name")
            subject = project_settings.SUBJECT + " " + queryset[0]["name"].lower()

            list_img = list_img if "list_img" in locals() else []
            mail_data = dataSave.data
            mail_data["list_img"] = list_img
            mail_data["len_img"] = len(list_img)
            mail_data["parentDepart"] = user_token['parentDepart']
            mail_data["agency"] = user_token['agency']

            # Nếu gửi email không phải trên production thì thêm thông báo xin hãy bỏ qua
            if project_settings.APP_ENVIRONMENT == 'production':
                mail_data["app_env_production"] = True

                #  Chuyển tới group mail quy trình để duyệt trước khi xuất bản theo ý a Tuấn Hồ
                #  (Anh em PDX gắn email đại diện này 1 lần 1 trong đời.
                #  NS có biến đổi thì Chị Mai Hà sẽ tự động sx lại.)
                recipient_list = ['FTEL.TINPNC.QUYTRINH@fpt.com']
            else:
                mail_data["app_env_production"] = False
                recipient_list = ['phuongnam.hadh@fpt.net']

            try:
                HandleMail(subject=subject, message="improved_car.html",
                           recipient_list=recipient_list, mail_data=mail_data).start()
            except Exception as ex:
                print("Error send email api post_blog", ex)
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, data_output=dataSave.data['id'], api_name="post_blog", message=SUCCESS['CREATE_BLOG']))
            thread.start()
            return response_data(message=SUCCESS['CREATE_BLOG'], data=dataSave.data['id'])
        thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="post_blog", status_code=4, message=dataSave.errors))
        thread.start()
        return response_data(message=dataSave.errors, status=4)

    @extend_schema(
        operation_id='Lấy đánh giá bài viết qua link',
        summary='Lấy đánh giá bài viết qua link',
        tags=["1. Xe cải tiến"],
        description='Lấy đánh giá bài viết qua link',
        responses=None,
        deprecated=True
    )
    def post_evaluate_idea(self, request):
        data = request.data.copy()
        if "link" not in data:
            return response_data(status=4, message="phải truyền link", data={})
        url = data["link"]
        try:
            payload = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            return response_data(json.loads(response.text)["data"])
        except Exception:
            return response_data(status=4, message="get không thành công", data={})

    @extend_schema(
        operation_id='Viết bình luận',
        summary='Viết bình luận',
        tags=["1. Xe cải tiến"],
        request=CommentVaidate,
        description='Viết bình luận',
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Thêm mới thành công",
                    "data": None
                }
            )
        }
    )
    def create_comment(self, request):
        data = request.data.copy()
        data_input = dict(data)
        # print(data_input)
        email = get_data_from_token(request)
        if email is None:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="create_comment", status_code=5, message=ERROR['TOKEN_NO_INFO']))
            thread.start()
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        data["email"] = email["email"]
        data["create"] = datetime.now()
        serializer = CommentVaidate(data=data)
        if not serializer.is_valid():
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="create_comment", status_code=5, message=serializer.errors))
            thread.start()
            return response_data(status=5, message=serializer.errors)
        dataSave = ImprovedCarCommentSerializer(data=data)
        if dataSave.is_valid():
            data_output = dataSave.validated_data
            data_output["t_create"] = str(dataSave.validated_data["t_create"])
            dataSave.save()
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, data_output=data_output, api_name="create_comment", message=SUCCESS['ADD']))
            thread.start()
            return response_data(message=SUCCESS['ADD'])
        thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="create_comment", status_code=4, message=dataSave.errors))
        thread.start()
        return response_data(message=dataSave.errors, status=4)

    @extend_schema(
        operation_id='Sửa bình luận',
        summary='Sửa bình luận',
        tags=["1. Xe cải tiến"],
        description='Sửa bình luận',
        request=ImprovedCarCommentSerializer,
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Thêm mới thành công",
                    "data": None
                }
            )

        }
    )
    def edit_comment(self, request):
        data = request.data.copy()
        email = get_data_from_token(request)
        if email is None:
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        if 'id' not in data:
            return response_data(status=5, message=ERROR['REQUIRED_ID'])
        try:
            queryset = ImprovedCarComment.objects.get(id=data['id'])
        except:
            return response_data(message=ERROR['SERVER'], status=4)

        dataSave = ImprovedCarCommentSerializer(queryset, data=data)
        if dataSave.is_valid():
            if dataSave.data['email'] != email['email']:
                return response_data(status=5, message=ERROR['NO_RIGHT_EDIT'])
            dataSave.save()
            return response_data(message=SUCCESS['UPDATE'])
        return response_data(message=ERROR['SERVER'], status=4)

    @extend_schema(
        operation_id='Xóa bình luận',
        summary='Xóa bình luận',
        tags=["1. Xe cải tiến"],
        description='Xóa bình luận',
        request=ImprovedCarCommentSerializer,
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Xóa thành công",
                    "data": None
                }
            )
        }
    )
    def detele_comment(self, request):
        data = request.data
        data_input = data
        email = get_data_from_token(request)
        if email is None:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="detele_comment", status_code=5, message=ERROR['TOKEN_NO_INFO']))
            thread.start()
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        if 'id' not in data:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="detele_comment", status_code=5, message=ERROR['REQUIRED_ID']))
            thread.start()
            return response_data(status=5, message=ERROR['REQUIRED_ID'])
        try:
            queryset = ImprovedCarComment.objects.filter(id=data['id'])
            validate = ImprovedCarCommentSerializer(queryset, many=True)
            if validate is None or validate == []:
                thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="detele_comment", status_code=5, message=ERROR['NO_CHOOSE_ROW']))
                thread.start()
                return response_data(status=5, message=ERROR['NO_CHOOSE_ROW'])
            if validate.data[0]["email"] != email["email"]:
                thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="detele_comment", status_code=5, message=ERROR['NO_RIGHT_DELETE']))
                thread.start()
                return response_data(status=5, message=ERROR['NO_RIGHT_DELETE'])
            queryset.update(deleted_at=datetime.now())
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_name="detele_comment", message=SUCCESS['UPDATE']))
            thread.start()
            return response_data(message=SUCCESS['UPDATE'], status=1)
        except:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="detele_comment", status_code=4, message=ERROR['SERVER']))
            thread.start()
            return response_data(message=ERROR['SERVER'], status=4)

    def like_status(self, id, email):
        queryset = ImprovedCarLike.objects.filter(id_tree=id, email=email)
        serializer = ImprovedCarLikeSerializer(queryset, many=True)
        if serializer.data == []:
            queryset.create(id_tree=id, email=email, state_like=0)

    @extend_schema(
        operation_id='Thích bài viết',
        summary='Thích bài viết',
        tags=["1. Xe cải tiến"],
        description='Thích bài viết',
        request=ImprovedCarLikeSerializer,
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Cập nhật thành công",
                    "data": None
                }
            )
        }
    )
    def do_like(self, request):
        data = request.data.copy()
        data_input = data
        if 'id' not in data:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="do_like", status_code=5, message=ERROR['REQUIRED_ID']))
            thread.start()
            return response_data(status=5, message=ERROR['REQUIRED_ID'])
        email = get_data_from_token(request)
        if email is None:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="do_like", status_code=5, message=ERROR['TOKEN_NO_INFO']))
            thread.start()
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        data["email"] = email["email"]
        serializer = LikeValidate(data=data)
        if not serializer.is_valid():
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="do_like", status_code=5, message=serializer.errors))
            thread.start()
            return response_data(status=5, message=serializer.errors)
        try:
            data_detail = {}
            self.like_status(id=data['id'], email=email['email'])
            queryset = ImprovedCarLike.objects.filter(id_tree=data['id'], email=email['email'])
            serializer = ImprovedCarLikeSerializer(queryset, many=True)
            if serializer.data[0]['state_like'] == 1:
                queryset.update(state_like=0)
                data_detail = {
                    "old_value": {
                        "state_like": serializer.data[0]['state_like']
                    },
                    "new_value": {
                        "state_like": queryset.values()[0]['state_like']
                    }
                }
                thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_name="do_like", message=SUCCESS['UPDATE'], data_detail=data_detail))
                thread.start()
                return response_data(message=SUCCESS['UPDATE'], status=1)
            queryset.update(state_like=1)
            data_detail = {
                "old_value": {
                    "state_like": serializer.data[0]['state_like']
                },
                "new_value": {
                    "state_like": queryset.values()[0]['state_like']
                }
            }
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_name="do_like", message=SUCCESS['UPDATE'], data_detail=data_detail))
            thread.start()
            return response_data(message=SUCCESS['UPDATE'], status=1)
        except:
            thread = threading.Thread(api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="do_like", status_code=4, message=ERROR['SERVER']))
            thread.start()
            return response_data(message=ERROR['SERVER'], status=4)

    def change_blogs_process_status(self, request):
        data = request.data
        ids = data.get('ids', [])
        if not ids or not ImprovedCar.objects.filter(id__in=ids).exists():
            return response_data(status=0, message="Danh sách ID xe cải tiến không tồn tại")

        processStatus = data.get('processStatus', None)
        if not processStatus or processStatus not in ('publish', 'unpublish', 'deleted'):
            return response_data(status=0, message="Trạng thái xe cải tiến không tồn tại")
        try:
            lst_improve_car = ImprovedCar.objects.filter(id__in=ids).exclude(process_status=processStatus)

            # Nếu cập nhật trạng thái từ unpublish sang publish thì gửi mail đến BGĐ
            if processStatus == 'publish':
                # Nếu gửi email không phải trên production thì thêm thông báo xin hãy bỏ qua
                if project_settings.APP_ENVIRONMENT == 'production':
                    app_env_production = True
                else:
                    app_env_production = False

                # Danh sách gửi email chung
                recipient_list = call_other_service_api(
                    service_call='profile_api',
                    end_point='get_features_roles_emails_improve_car',
                    data={
                        "role_codes": [ROLE_CODE_NHAN_VIEN_DANH_GIA]
                    }
                )
                recipient_list = recipient_list or []

                # Danh sách gửi email là TIN
                recipient_list_tin = call_other_service_api(
                    service_call='profile_api',
                    end_point='get_features_roles_emails_improve_car',
                    data={
                        "role_codes": [ROLE_CODE_NHAN_VIEN_DANH_GIA_TIN]
                    }
                )
                recipient_list_tin = recipient_list_tin or []
                # Danh sách gửi email là PNC
                recipient_list_pnc = call_other_service_api(
                    service_call='profile_api',
                    end_point='get_features_roles_emails_improve_car',
                    data={
                        "role_codes": [ROLE_CODE_NHAN_VIEN_DANH_GIA_PNC]
                    }
                )
                recipient_list_pnc = recipient_list_pnc or []

                # lấy danh sách email gửi từ phòng ban PDX (PCDSDX)
                data_pdx_lst_email = call_other_service_api(
                    service_call='profile_api',
                    end_point='get_list_email_pdx'
                )
                data_pdx_lst_email = data_pdx_lst_email or []
                pdx_lst_email = [e.lower() for e in data_pdx_lst_email]

                improve_car_group_list = ImprovedCarGroup.objects.values("id", "name")
                improve_car_group_dict = {g['id']: g['name'].lower() for g in improve_car_group_list}

                for improve_car in lst_improve_car:
                    if improve_car.process_status == 'unpublish':
                        list_img = [item for item in (improve_car.img_xe_cai_tien or '').split(";") if item != '']
                        mail_data = {
                            'app_env_production': app_env_production,
                            'id': improve_car.id,
                            'updateTime': improve_car.update_time.strftime("%H:%M"),
                            'updateDate': improve_car.update_time.strftime("%d-%m-%Y"),
                            'emailCreate': improve_car.email_create,
                            'nameImprovedCar': improve_car.name_xe_cai_tien,
                            'currentStatus': improve_car.current_status,
                            'purpose': improve_car.purpose,
                            'solution': improve_car.solution,
                            "list_img": list_img,
                            "len_img": len(list_img),
                            "parentDepart": improve_car.parent_depart,
                            "agency": improve_car.agency
                        }
                        if improve_car.email_create.lower() in pdx_lst_email:
                            # nếu là email pdx thì gửi đến ftel pnc pdx
                            if project_settings.APP_ENVIRONMENT == 'production':
                                recipients = ['tinpnc.cdsmn@fpt.net']
                            # ngược lại gửi vào account dev hadh
                            else:
                                recipients = ['phuongnam.hadh@fpt.net']
                        else:
                            recipients = list(recipient_list)  # deepcopy danh sach email gui ca TIN va PNC
                            if improve_car.branch == "TIN":
                                recipients.extend(recipient_list_tin)
                            if improve_car.branch == "PNC":
                                recipients.extend(recipient_list_pnc)

                        subject = project_settings.SUBJECT + " " + improve_car_group_dict[improve_car.type_title]
                        try:
                            HandleMail(subject=subject, message="improved_car.html",
                                       recipient_list=recipients, mail_data=mail_data).start()
                        except Exception as ex:
                            print("Error send email api change_status_improve_car:", ex)
            lst_improve_car.update(
                process_status=processStatus)
        except Exception as ex:
            print('Cập nhật trạng thái bài viết không thành công:', ex)
            return response_data(status=0, message='Cập nhật trạng thái bài viết không thành công')
        return response_data(status=1, message='Cập nhật trạng thái bài viết thành công')
