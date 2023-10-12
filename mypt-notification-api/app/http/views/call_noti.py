import threading
from rest_framework.viewsets import ViewSet
from core.helpers.noti import *
from core.helpers.response import *
from ..validations.validate import *
from ..serializers.notification_serializer import *
from django.conf import settings as project_settings
from datetime import datetime, timedelta
from ..models.notification import Notification
from django.db.models import Q
from core.helpers.configs import get_config, remove_config
import asyncio
from django.http import HttpResponse
from asgiref.sync import sync_to_async
from django.db import close_old_connections


class CallNotiView(ViewSet):
    def service_send_noti(self, request):
        data = request.data.copy()
        data_time = datetime.now()
        data['id'] = data_time.strftime("%d%H%M%S")
        validate = ServiceSendNoti(data=data)
        if not validate.is_valid():
            return response_data(status=5, message="error", data=validate.errors)
        send_notification = send_noti(data=data)
        if "failure" in send_notification and send_notification["failure"] > 0:
            return response_data(send_notification)
        return self.save_notification(request.data)
    
    def save_notification(self, data={}, str_time_now=None):
        topic_type = data.get("topic_type", None)
        if topic_type in ['all', 'love', 'checkin', 'HTKT', 'idea', 'media', 'noti_base', 'PTQ']:
            content = data.get("body", "")
            data_time = datetime.now()
            str_time_now = data_time.strftime('%Y-%m-%d %H:%M:%S') if str_time_now == None else str_time_now
            data['send_at'] = str_time_now
            url_noti = data.get("notifyDataAction",None)
            action_noti =  data.get("notifyActionType",None)
            url_popup = data.get("popupDetailDataAction",None)
            action_popup =  data.get("popupDetailActionType",None)
            if url_noti == "":
                url_noti = None
            if url_popup == "":
                url_popup = None
            result = {
                "title":data.get("title", ""),
                "email" : data.get("email", ""),
                "contentShort" : content,
                "content" : content,
                "contentLong" : content,
                "isReaded" : 0,
                "direction" : "popup",#data["navigate"],
                "receivedAt" : None,
                # "createdAt" : None,
                # "updatedAt" : None,
                "is_send" : 0,
                "send_at": str_time_now,
                "is_readed" : 0,
                "is_fake":0,
                "process_status" : "publish",
                "topic_type": data.get("topic_type", "noti_base"),
                "data_action": url_noti,
                "action_type": action_noti,            
                "popup_data_action": url_popup,
                "popup_action_type": action_popup,
                "sender_id": data.get("sender_id", None),
                "receive_device_id": data.get("receive_device_id", None),
                "data_input": data.get("data_input", None),
                "priority": data.get("priority", 0)
            }
            dataSave = SaveNotification(data=result)
            # try:
            if dataSave.is_valid():
                dataSave.save()
                return response_data(message="add ok", data=dataSave.data)
            print(dataSave.errors)
            return response_data(status=5, message=dataSave.errors)
        return response_data()

    def service_list_code(self, request):
        try:
            data = request.data.copy()
            validate = ListCodeValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message="error", data=validate.errors)
            structure = data
            
            list_code = structure.pop("empCode")
            list_email = self.email_to_code(list_code=list_code)
            header = get_data(list_item=NOTI_MUTI_HEAD, structure=structure)
            data_structure = get_data(list_item=NOTI_DATA, structure=structure)

            data_structure["registration_ids"] = self.list_device_token(list_email=list_email)
            print(data_structure["registration_ids"])
            if "to" in data_structure:
                data_structure.pop("registration_ids")

            return response_data(send_structure_noti(data=data_structure))
        except Exception as e:
            print("---", e)
            return response_data(status=4, message=str(e))
    
    def email_to_code(self, list_code=[]):
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        host = SERVICE_CONFIG["profile"][app_env]
        func = SERVICE_CONFIG["profile"]["email-to-list-code"]['func']
        method = SERVICE_CONFIG["profile"]["email-to-list-code"]['method']
        headers = {'Content-Type': 'application/json'}
        data = {"empCode":list_code}
        payload = json.dumps(data)
        response = requests.request(method, host+func, headers=headers, data=payload)
        data_api = json.loads(response.text)
        if data_api["statusCode"] != 1:
            return ""
        data_api = data_api['data']
        list_email = []
        for item in data_api:
            list_email.append(item["email"])
        return list_email
    
    def email_from_token(self, list_device):
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        host = SERVICE_CONFIG["auth"][app_env]
        func = SERVICE_CONFIG["auth"]["get-emails-by-device-tokens"]['func']
        method = SERVICE_CONFIG["auth"]["get-emails-by-device-tokens"]['method']
        headers = {'Content-Type': 'application/json'}
        data = {"deviceTokens":list_device}
        payload = json.dumps(data)
        response = requests.request(method, host+func, headers=headers, data=payload)
        data_api = json.loads(response.text)
        if data_api["statusCode"] != 1:
            return None
        data_api = data_api['data']['usersList']
        return data_api
    
    def variable(self, request):
        return request.data
        
    def send_muti_noti(self, request):
        data_data = request.data.copy()
        list_device = []
        data_save = []
        success = 0
        failure = 0
        try:
            for key in data_data["data"]:
                list_device.append(key["deviceToken"])
            list_email = self.email_from_token(list_device)
            for item in data_data['data']:
                data_save.append(item.copy())
                data_time = datetime.now()
                item['id'] = data_time.strftime("%d%H%M%S")
                structure_noti = notification_structure_base(item)
                result = send_structure_noti(data=structure_noti)
                failure += result["failure"]
                success += result["success"]
            if list_email is not None:
                for value in list_email:
                    expectedResult = [d for d in data_save if d['deviceToken'] == value["deviceToken"]]
                    expectedResult[0]["email"] = value["email"]
                    self.save_notification(expectedResult[0])
            # return response_data(expectedResult)
        except Exception as e:
            print(e)
            return response_data(str(e), status=4)
        return response_data({
            "failure":failure,
            "success":success
        })
              
    def send_multiple_notify_with_the_same_content_by_list_email_no_save(self, request):
        try:
            data = request.data.copy()
            validate = ListEmailValidate(data=data)
            if not validate.is_valid():
                return response_data(status=4, message="error", data=validate.errors)
            structure = data
    
            list_email = structure.pop("list_email", [])
            list_set = set(list_email)
            list_email = list(list_set)
            
            if len(list_email) > 1000:
                return response_data("over_size", status=4, message="Giới hạn số lượng email là 1000!")
            list_device_info = get_list_user_device_info_by_email(list_email=list_email)
            sender_id = None
            data_time = datetime.now()
            str_time_now = data_time.strftime('%Y-%m-%d %H:%M:%S')
            list_device_token = []

            for device_info in list_device_info:
                list_device_token.append(device_info['deviceToken'])
            
            header = get_data(list_item=NOTI_MUTI_HEAD, structure=structure)
            data_structure = get_data(list_item=NOTI_DATA, structure=structure)
            data_structure["registration_ids"] = list_device_token
            if "registration_ids" in data_structure or "to" in data_structure:
                data_structure.pop("to", None)

            return response_data(send_structure_noti(data=data_structure), message=data_structure)
        except Exception as e:
            print(e)
            return response_data(data={"message": " Service Unavailable!"}, status=4, message=str(e))
      
    def send_multiple_notify_with_the_same_content_by_list_email(self, request):
        try:
            data = request.data.copy()
            topic_type_check = data.get('topic_type', None) in ['all', 'love', 'checkin', 'HTKT', 'idea', 'media', 'noti_base', 'PTQ']
            
            if not topic_type_check:
                return response_data(data='topic_type', status=4, message="'topic_type' is required")
            
            validate = ListEmailValidate(data=data)
            
            if not validate.is_valid():
                return response_data(status=4, message="error", data=validate.errors)
            
            save_data = data.copy()
            save_data.pop("list_email", None)
            list_email = data.pop("list_email", [])
            list_set = set(list_email)
            list_email = list(list_set)
            
            if len(list_email) > 1500:
                return response_data("over_size", status=4, message="Giới hạn số lượng email là 1500!")
            list_device_info = get_list_user_device_info_by_email(list_email=list_email)
            sender_id = None
            data_time = datetime.now()
            str_time_now = data_time.strftime('%Y-%m-%d %H:%M:%S')
            list_device_token = []

            for user_email in list_email:
                for device_info in list_device_info:
                    if device_info.get('email', None) == user_email:
                        try:
                            structure = data.copy()
                            structure['deviceToken'] = device_info.get("deviceToken", "")
                            save_data['email'] = user_email
                            save_data['receive_device_id'] = device_info.get("deviceId")
                            save_data["sender_id"] = sender_id
                            list_device_token.append(device_info.get('deviceToken', None))
                            noti_id = self.save_notification(save_data, str_time_now).data['data']['id']
                            structure['sender_id'] = sender_id
                            structure['send_at'] = str_time_now
                            structure['noti_id'] = noti_id
                            structure_noti = notification_structure_base(structure)
                            structure_noti.pop("registration_ids", None)
                            structure_noti = json.dumps(structure_noti)
                            curr_noti = Notification.objects.get(id=noti_id)
                            curr_noti.data_input = structure_noti
                            curr_noti.save()
                        except Exception as e:
                            print(e)
                            continue

            return response_data()
        except Exception as e:
            print(e)
            return response_data(data={"message": " Service Unavailable!"}, status=4, message=str(e))
        
    def send_multiple_notify_with_the_different_content_by_list_email(self, request):
        try:
            data = request.data.copy()
            if len(data) > 1000:
                return response_data("over_size", status=4, message="Giới hạn số lượng thông báo được phép gửi đi là 1000!")
            list_email = []
            for item in data:
                user_email = item.get("email", None)
                if user_email == None:
                    return response_data(data="lack_of_email", status=4, message="Dữ liệu đầu vào thiếu email người nhận thông báo!")
                list_email.append(user_email)
            list_device_info = get_list_user_device_info_by_email(list_email)
            
            if isinstance(list_device_info, str):
                return response_data(data="get_list_device_failure", status=4, message="Lỗi hệ thống!")

            sender_id = None
            for device_info in list_device_info:
                for notify_content in data:
                    if notify_content.get('email', "-") == device_info.get('email', "--"):
                        try:
                            topic_type_check = notify_content.get('topic_type', None) in ['all', 'love', 'checkin', 'HTKT', 'idea', 'media', 'noti_base', 'PTQ']
                            notify_content['sender_id'] = sender_id
                            notify_content['receive_device_id'] = device_info.get('deviceId', None)
                            noti_id = None
                            if topic_type_check:
                                save_data = self.save_notification(notify_content)
                                noti_id = save_data.data['data']['id']
                            notify_content['noti_id'] = noti_id
                            device_token = device_info.get("deviceToken", None)
                            notify_content["deviceToken"] = device_token
                            data_time = datetime.now()
                            notify_content['id'] = data_time.strftime("%d%H%M%S")
                            structure_noti = notification_structure_base(notify_content)
                            structure_noti.pop("registration_ids", None)
                            notify_content['data_input'] = json.dumps(structure_noti)
                            if noti_id:
                                curr_noti = Notification.objects.get(id=noti_id)
                                curr_noti.data_input = notify_content['data_input']
                                curr_noti.save()
                        except Exception as e:
                            print(e)
                            continue
            
            return response_data(message="Thành công!")
        except Exception as e:
            print(e)
            return response_data(data={"error": str(e)}, status=4, message="Lỗi hệ thống!")
        
    def send_one_noti(self, request):
        try:
            data = request.data.copy()
            validate = EmailValidate(data=data)
            
            if not validate.is_valid():
                return response_data(status=4, message=validate.errors)
            
            email = data.pop('email', None)
            user_info = get_user_device_info_by_email(email)
            
            if not user_info:
                return response_data(data="no_data", status=4)
            
            device_token = user_info['deviceToken']
            receive_device_id = user_info['deviceId']
            noti_data = data
            noti_data['deviceToken'] = device_token
            noti_data['email'] = email
            noti_data['receive_device_id'] = receive_device_id
            save_noti_data = self.save_notification(noti_data).data
            noti_id = save_noti_data['data'].get('id', None)
            
            if save_noti_data['status'] != 1:
                return response_data(status=4, message="can't save notification")
            noti_data['noti_id'] = noti_id
            noti_data['id'] = datetime.now().strftime("%d%H%M%S")
            data_structure = notification_structure_base(noti_data)
            data_structure.pop("registration_ids", None)
            
            if noti_id:
                curr_noti = Notification.objects.get(id=noti_id)
                curr_noti.data_input = json.dumps(data_structure)
                curr_noti.save()
            else: 
                send_structure_noti(data=json.dumps(data_structure))
            return response_data()
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))
    
    def update_noti_properties(self, request):
        allow_tracking = get_config("ALLOW_TRACKING")
        if allow_tracking:
            try:
                # return response_data()
                data = request.data.copy()
                update_validate = NotificationUpdateSerializer(data=data)
                
                if not update_validate.is_valid():
                    return response_data(status=4, message=update_validate.errors)
                
                update_data = update_validate.data
                noti_identify_validate = NotificationIdentifySerializer(data=update_data['noti_identify'])
                
                if not noti_identify_validate.is_valid():
                    return response_data(status=4, message=noti_identify_validate.errors)
                elif (noti_identify_validate.data['noti_id'] == None) and \
                    (noti_identify_validate.data['sender_id'] == None or \
                    noti_identify_validate.data['send_at'] == None or \
                    noti_identify_validate.data['device_id'] == None):
                    return response_data(status=4, message="noti_identify_is_invalid") 
                
                noti_identify = noti_identify_validate.data
                
                noti = None
                
                if noti_identify['noti_id']:
                    noti = Notification.objects.get(id=noti_identify['noti_id'])
                else: 
                    if noti_identify['sender_id']:
                        noti = Notification.objects.filter(
                            sender_id=noti_identify['sender_id'], 
                            send_at=noti_identify['send_at'],
                            receive_device_id=noti_identify['device_id']
                        ).first()
                    else:
                        noti = Notification.objects.filter(
                            send_at=noti_identify['send_at'],
                            receive_device_id=noti_identify['device_id']
                        ).first()

                if noti:
                    data.pop("noti_identify", None)
                    keys = []
                    datas = {}
                    for key in data.keys():
                        keys.append(key)
                        if data[key] != None:
                            datas[key] = data[key]
                            setattr(noti, key, data[key])
                        
                    noti.save()
                    return response_data(
                        {
                            "input": data,
                            "keys": keys,
                            "datas": datas
                        }
                    )        

                return response_data(status=4, message="notify unknown")
            except Exception as e:
                print(e)
                return response_data(status=4, message=str(e))
        else:
            return response_data("NO_ALLOW_TRACKING")
        
    def remove_config(self, request):
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
        
    def get_config(self, request):
        try:
            data = request.data.copy()
            if "config_key" not in data:
                return response_data("no_config_key", status=4)
            
            config_key = data["config_key"]
            
            return response_data(get_config(config_key))
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))

async def cron_send_noti(request):
    try:
        query_limit = 300
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        
        query_noti_valid =  Q(is_send=0) \
            & ~(Q(data_input=None) | Q(data_input=""))
        query_noti_unsent = Q(result_call_api=None) | Q(result_call_api="")
        query_noti_send_failed = ~(Q(result_call_api=None) | Q(result_call_api="")) \
            & Q(created_at__gte=today) \
            & ~(Q(result_call_api__icontains="InvalidRegistration") \
                | Q(result_call_api__contains="InvalidRegistration"))
        
        query_noti_valid = Notification.objects.filter(query_noti_valid)
        queryset_unsent_noti = query_noti_valid\
            .filter(query_noti_unsent) \
            .order_by('-priority') \
            .order_by('created_at')[:query_limit]
        
        num_noti_send_failed = query_limit - len(queryset_unsent_noti) + 20
        queryset_noti_send_failed = query_noti_valid\
            .filter(query_noti_send_failed)\
            .order_by('-priority')\
            .order_by('created_at')[:num_noti_send_failed]
            
        loop = asyncio.get_event_loop()
        async_tasks = []
        
        for noti in queryset_unsent_noti:
            noti_data = noti.data_input
            async_task = sync_to_async(send_structure_noti, thread_sensitive=False)
            
            async_tasks.append(loop.create_task(async_task(noti, noti_data)))
            print("done")
            
        for noti in queryset_noti_send_failed:
            noti_data = noti.data_input
            async_task = sync_to_async(re_send_noti_send_failed, thread_sensitive=False)
            
            async_tasks.append(loop.create_task(async_task(noti, noti_data)))
            print("done")
        
        responses = await asyncio.gather(*async_tasks)
        
        close_old_connections()
        
        return HttpResponse(responses)
    except Exception as e:
        print(e)
        return HttpResponse(str(e))
    