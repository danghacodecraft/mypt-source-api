import ast

import redis
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from http.paginations.custom_pagination import *
from ..serializers.ptq_serializer import *
from ..validations.ptq_validate import *
from core.helpers.response import *
from rest_framework.viewsets import ViewSet
from datetime import *
from core.helpers.utils_call_api import *


class PtqView(ViewSet):
    throttle_classes = []

    def get_throttles(self):
        return self.throttle_classes

    @extend_schema(
        operation_id='Đếm kiểm soát màn hình home',
        summary='Đếm kiểm soát màn hình home',
        tags=["2. Kiểm soát"],
        description='Đếm kiểm soát màn hình home',
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Success",
                    "data": {
                        "deadline": 0,
                        "needExplanation": 0,
                        "addExplanation": 0
                    }
                }
            )
        }
    )
    def home_count_ptq(self, request):
        data = request.data.copy()
        email = get_data_from_token(request)
        if email is None:
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        email = email["email"]
        queryset = Ptq.objects.filter(deleted_at__isnull=True, email=email)
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id', 'description',
                                                                                          'type')
        # fix bug home count
        rule_deadline = rule.filter(type__in=["NOTOK", "ADD"]).values_list('id', flat=True)
        rule_need = rule.filter(type__in=["NOTOK"]).values_list('id', flat=True)

        rule_add = rule.filter(type="ADD").values_list('id', flat=True)
        count_deadline = queryset.filter(deadline__in=[date_from_now(), date_from_now(1)],
                                         recorded__in=rule_deadline).count()
        need_explanation = queryset.filter(deadline__gt=date_from_now(-1), recorded__in=rule_need).count()
        add_explanation = queryset.filter(recorded__in=rule_add).count()
        result = {
            "deadline": count_deadline,
            "needExplanation": need_explanation,
            "addExplanation": add_explanation
        }

        return response_data(data=result)

    @extend_schema(
        operation_id='Đếm kiểm soát màn hình home version 2',
        summary='Đếm kiểm soát màn hình home version 2',
        tags=["2. Kiểm soát"],
        description='Đếm kiểm soát màn hình home version 2',
        # parameters=None,
        responses={
            200: OpenApiResponse(
                description='Example',
                response={
                    "statusCode": 1,
                    "message": "Success",
                    "data": {
                        "deadline": {
                            "data": 0,
                            "name": "Sắp hết hạn",
                            "type": "ALL",
                            "searchKey": [
                                2,
                                7,
                            ]
                        },
                        "needExplanation": {
                            "data": 0,
                            "name": "Chưa giải trình",
                            "type": "NOTOK",
                            "searchKey": [
                                2
                            ]
                        },
                        "addExplanation": {
                            "data": 0,
                            "name": "Bổ sung giải trình",
                            "type": "ADD",
                            "searchKey": [
                                7
                            ]
                        }
                    }
                }
            )
        }
    )
    def home_count_ptq_2(self, request):
        data = request.data.copy()
        email = get_data_from_token(request)
        if email is None:
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        email = email["email"]
        queryset = Ptq.objects.filter(deleted_at__isnull=True, email=email)
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id', 'description', 'type')
        # fix bug home count
        rule_deadline = rule.filter(type__in=["NOTOK", "ADD"]).values_list('id', flat=True)
        rule_need = rule.filter(type__in=["NOTOK"]).values_list('id', flat=True)

        rule_add = rule.filter(type="ADD").values_list('id', flat=True)
        count_deadline = queryset.filter(deadline__in=[date_from_now(), date_from_now(1)],
                                         recorded__in=rule_deadline).count()
        need_explanation = queryset.filter(deadline__gt=date_from_now(-1), recorded__in=rule_need).count()
        add_explanation = queryset.filter(recorded__in=rule_add).count()
        type_notok = PtqType.objects.get(type='NOTOK')
        type_add = PtqType.objects.get(type='ADD')
        result = {
            "deadline": {
                "data": count_deadline,
                "name": "Sắp hết hạn",
                "type": "ALL",
                "searchKey": PtqType.objects.all().filter(type__in=["NOTOK", "ADD"]).values_list('id', flat=True),
                "searchDate": [date_from_now_mobile(-1), date_from_now_mobile()]
            },
            "needExplanation": {
                "data": need_explanation,
                "name": type_notok.description,
                "type": type_notok.type,
                "searchKey": PtqType.objects.filter(type="NOTOK").values_list('id', flat=True),
                # "searchDate" : [date_from_now(), date_from_now(100)]
            },
            "addExplanation": {
                "data": add_explanation,
                "name": type_add.description,
                "type": type_add.type,
                "searchKey": PtqType.objects.filter(type="ADD").values_list('id', flat=True),
                # "searchDate" : ["", ""]
            }
        }
        return response_data(data=result)

    @extend_schema(
        operation_id='Danh sách kiểm soát',
        summary='Danh sách kiểm soát',
        tags=["2. Kiểm soát"],
        description='Danh sách kiểm soát',
        request=PtqSerializer,
        responses={
            status.HTTP_200_OK: None,
        }
    )
    def history_ptq(self, request):
        data = request.data.copy()
        email = get_data_from_token(request)
        if email is None:
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="history_ptq",
                         status_code=5, message=ERROR['TOKEN_NO_INFO'])
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        email = email["email"]
        queryset = Ptq.objects.filter(email=email)
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id', 'description', 'type')
        rule_deadline = rule.filter(type__in=["NOTOK", "ADD"]).values_list('id', flat=True)
        # pnc check giải trình đã gửi phê duyệt
        deadline_query = queryset.filter(deadline__in=[date_from_now(), date_from_now(1)], recorded__in=rule_deadline)
        deadline_query_lst_id = deadline_query.values_list('id')

        not_deadline_query = queryset.exclude(id__in=deadline_query_lst_id)

        date_range = DateValidate(data=data)
        month_range = MonthValidate(data=data)
        type_id = ListTypeValidate(data=data)
        if month_range.is_valid():
            first_date, last_date = month_from_now(data["month"])
            not_deadline_query = not_deadline_query.filter(created_at__date__range=(first_date, last_date))
        elif date_range.is_valid():
            first_date = date_range.data["dateStart"]
            last_date = date_range.data["dateEnd"]
            if datetime.strptime(first_date, DATE_FORMAT_QUERY) > datetime.strptime(last_date, DATE_FORMAT_QUERY):
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="history_ptq",
                             status_code=4, message=ERROR["DATE_START"])
                return response_data(status=4, message=ERROR["DATE_START"])
            if datetime.strptime(last_date, DATE_FORMAT_QUERY) > datetime.now():
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="history_ptq",
                             status_code=4, message=ERROR["DATE_NOW"])
                return response_data(status=4, message=ERROR["DATE_NOW"])
            not_deadline_query = not_deadline_query.filter(created_at__date__range=(first_date, last_date))
        date_range.is_valid()
        if type_id.is_valid():
            rule_id = rule.filter(id__in=type_id.data["typeId"]).values_list('id', flat=True)
            not_deadline_query = not_deadline_query.filter(recorded__in=rule_id)
            deadline_query = deadline_query.filter(recorded__in=rule_id)

        message_error = [
            date_range.errors,
            month_range.errors,
            type_id.errors
        ]
        all_query = deadline_query.union(not_deadline_query)
        paginator = PtqPagination()
        query_count = not_deadline_query.count() + deadline_query.count()
        per_page = paginator.page_size
        count = query_count // per_page
        if query_count % per_page > 0:
            count += 1

        paginator_query = paginator.paginate_queryset(all_query, request)
        list_control = PtqSerializer(paginator_query, many=True, not_fields=["deletedAt"])

        result = {
            "numberPage": count,
            "listControl": list_control.data
        }
        api_save_log(request=request, data_input=data, data_output=result, api_name="history_ptq",
                     message=str(message_error))
        return response_data(data=result, message=str(message_error))

    @extend_schema(
        operation_id='Lấy danh sách loại kiểm soát',
        summary='Lấy danh sách loại kiểm soát',
        tags=["2. Kiểm soát"],
        description='Lấy danh sách loại kiểm soát',
        responses={
            status.HTTP_200_OK: None
        }
    )
    def ptq_type(self, request):
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id', 'description', 'type')
        serializer = PtqTypeSerializer(rule, many=True, fields=['id', 'description', 'type'])
        list_recorded = serializer.data
        return response_data(list_recorded)

    @extend_schema(
        operation_id='Chi tiết kiểm soát',
        summary='Chi tiết kiểm soát',
        tags=["2. Kiểm soát"],
        description='Chi tiết kiểm soát',
        responses={
            status.HTTP_200_OK: None,
        }
    )
    def history_ptq_id(self, request):
        data = request.data.copy()
        email = get_data_from_token(request)
        if email is None:
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="history_ptq_id",
                         status_code=5, message=ERROR['TOKEN_NO_INFO'])
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        email = email["email"]
        validate = IdValidate(data=data)
        if not validate.is_valid():
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="history_ptq_id",
                         status_code=5, message=list(validate.errors.values())[0][0])
            return response_data(status=5, message=list(validate.errors.values())[0][0])
        if not Ptq.objects.filter(email=email, id=data["id"]).exists():
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="history_ptq_id",
                         status_code=4, message=ERROR['PTQ_EXISTS'])
            return response_data(status=4, message=ERROR['PTQ_EXISTS'])
        ptq_queryset = Ptq.objects.filter(email=email, id=data["id"])
        serializer = PtqSerializer(ptq_queryset, many=True, not_fields=["deletedAt"])
        ptq_data = serializer.data[0]
        history_queryset = PtqHistory.objects.filter(ptq_id=ptq_data["id"])
        serializer = PtqHistorySerializer(history_queryset, many=True, not_fields=["deletedAt"], image=True)
        ptq_history = serializer.data
        explanation = False
        is_deadline = False
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id', 'description', 'type')
        rule_deadline = rule.filter(type__in=["NOTOK", "ADD"]).values_list('id', flat=True)
        if ptq_queryset.filter(deadline__gt=date_from_now(-1), recorded__in=rule_deadline).exists():
            explanation = True

        if ptq_queryset.filter(
                Q(deadline=date_from_now(-1), recorded__in=[2, 7]) | Q(deadline=date_from_now(), recorded__in=[2, 7])
        ).exists():
            is_deadline = True
        result = {
            "ptq": ptq_data,
            "ptqHistory": ptq_history,
            "explanation": explanation,
            "is_deadline": is_deadline
        }
        api_save_log(request=request, data_input=data, data_output=result, api_name="history_ptq_id")
        return response_data(result)

    @extend_schema(
        operation_id='Giải trình kiểm soát',
        summary='Giải trình kiểm soát',
        tags=["2. Kiểm soát"],
        description='Giải trình kiểm soát',
        responses={
            status.HTTP_200_OK: None
        }
    )
    def explanation(self, request):
        data = request.data.copy()
        email = get_data_from_token(request)
        if email is None:
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="explanation",
                         status_code=5, message=ERROR['TOKEN_NO_INFO'])
            return response_data(status=5, message=ERROR['TOKEN_NO_INFO'])
        email = email["email"]
        # email = "anph13@fpt.com.vn"
        validate = ExplanationValidate(data=data)
        if not validate.is_valid():
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="explanation",
                         status_code=5, message=list(validate.errors.values())[0][0])
            return response_data(status=5, message=list(validate.errors.values())[0][0])
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id', 'description', 'type')
        rule_deadline = rule.filter(type__in=["NOTOK", "ADD"]).values_list('id', flat=True)
        ptq_queryset = Ptq.objects.filter(email=email, id=data["id"])
        if "action" not in data or data["action"] != "edit":
            if not ptq_queryset.filter(deadline__gt=date_from_now(-1), recorded__in=rule_deadline).exists():
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="explanation",
                             status_code=4, message=ERROR["EXPLANATION"])
                return response_data(status=4, message=ERROR["EXPLANATION"])
        data_save = {
            "content": data["content"],
            # "ptqId" : data["id"],
            "status": rule.filter(type__in=["TODO"]).values_list('id', flat=True)[0],
            # "times" : PtqHistory.objects.filter(ptq_id=data["id"]).count()+1
        }

        # up hinh
        # xu ly hinh anh
        # luu tru anh bang cach goi api
        if len(request.FILES.getlist('file')) > 0:
            status_code, msg_code, data_code = call_api_save_file_new(request, email, "explanation")
            if status_code == 1:
                list_img = data_code.get('linkFile')
                link_img = to_str_fr_list(list_img)
            else:
                print("---------------------UP HINH --------------------")
                # print(msg_code)
                try:
                    if status_code == 4:
                        api_save_log(request=request, data_input=data, data_output={}, api_status=0, err_analysis=0,
                                     api_name="explanation", status_code=status_code, message="Không thể up hình")
                    elif status_code == 5:
                        api_save_log(request=request, data_input=data, data_output={}, api_status=0, err_analysis=-1,
                                     api_name="explanation", status_code=status_code, message="Không thể up hình")
                except:
                    pass
                return response_data(data={}, message="Không thể up hình", status=status_code)
            data_save["image"] = link_img
        if "action" in data and data["action"] == "edit":
            fileUrlList = data['fileUrlList']
            data_save["image"] = fileUrlList
            try:
                explanation_queryset = PtqHistory.objects.get(id=data["id"])
            except:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="explanation",
                             status_code=5, message="Giai trinh khong ton tai")
                return response_data(status=5, message="Giai trinh khong ton tai")
            is_save = PtqHistorySerializer(explanation_queryset, data=data_save)
            if not is_save.is_valid():
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="explanation",
                             status_code=5, message=list(is_save.errors.values())[0][0])
                return response_data(status=5, message=list(is_save.errors.values())[0][0])
            is_save.save()
            api_save_log(request=request, data_input=data, data_output=is_save.data, api_name="explanation",
                         message=SUCCESS["EXPLANATION"])
            return response_data(message=SUCCESS["EXPLANATION"], data=is_save.data)

        data_save["ptqId"] = data["id"]
        data_save["times"] = PtqHistory.objects.filter(ptq_id=data["id"]).count() + 1
        is_save = PtqHistorySerializer(data=data_save)
        if not is_save.is_valid():
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="explanation",
                         status_code=5, message=list(is_save.errors.values())[0][0])
            return response_data(status=5, message=list(is_save.errors.values())[0][0])
        is_save.save()
        is_save = PtqSerializer(ptq_queryset.get(), data={"recorded": data_save["status"]})
        if not is_save.is_valid():
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="explanation",
                         status_code=5, message=list(is_save.errors.values())[0][0])
            return response_data(status=5, message=list(is_save.errors.values())[0][0])
        is_save.save()
        api_save_log(request=request, data_input=data, data_output=data_save, api_name="explanation",
                     message=SUCCESS["EXPLANATION"])
        return response_data(message=SUCCESS["EXPLANATION"], data=data_save)

    @extend_schema(
        operation_id='Lấy loại kiểm soát từ redis',
        summary='Lấy loại kiểm soát từ redis',
        tags=["3. Out API"],
        description='Lấy loại kiểm soát từ redis',
        responses={
            status.HTTP_200_OK: None
        }
    )
    def get_ptq_types_from_redis(self, request):
        redisInstance = redis.StrictRedis(host=project_settings.SERVICE_REDIS_HOST,
                                          port=project_settings.SERVICE_REDIS_PORT,
                                          db=project_settings.SETTING_REDIS_DATABASE,
                                          password=project_settings.SERVICE_REDIS_PASSWORD,
                                          decode_responses=True, charset="utf-8")

        ptqTypeStr = redisInstance.get("ptqTypes")
        if ptqTypeStr is None:
            # print("can tao lai Redis cho PTQ types!")
            qs = PtqType.objects.all()
            serializer = PtqTypeSerializer(qs, many=True)
            rows = serializer.data
            dataForRedis = []
            for row in rows:
                dataForRedis.append({"id": row.get("id"), "type": row.get("type"), "deletedAt": row.get("deletedAt")})
            redisInstance.set("ptqTypes", str(dataForRedis), 86400)
            return response_data(data=dataForRedis)
        else:
            # print("DA TON TAI Redis ptq types !")
            ptqTypeData = ast.literal_eval(ptqTypeStr)
            return response_data(data=ptqTypeData)

    @extend_schema(
        operation_id='Lấy loại kiểm soát theo email',
        summary='Lấy loại kiểm soát theo email',
        tags=["3. Out API"],
        description='Lấy loại kiểm soát theo email',
        responses={
            status.HTTP_200_OK: None
        }
    )
    def get_ptq_from_email(self, request):
        data = request.data

        if 'email' not in data or not data['email']:
            return response_data(data=[])

        ptq = Ptq.objects.filter(deleted_at__isnull=True, email=data['email']).values('deadline', 'recorded')

        return response_data(data=ptq)
