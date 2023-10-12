from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..validations.validate import NotificationValidator
from ...core.helpers.response import *
from rest_framework import status
from django.db import connection
from rest_framework.viewsets import ViewSet

from ..models.notification import *
from ..models.notification_topic import *
from ..models.notification_topic_group import *
from ..serializers.notification_serializer import *

from ...core.helpers.fcm import FCMApi
from ...core.helpers.utils import *
from ..paginations.custom_pagination import *
from ...core.helpers.auth_session_handler import getUserAuthSessionData
from django.conf import settings as project_settings
from datetime import datetime

class NotiView(ViewSet):
    def get_group(self, request):
        try:
            queryset = NotificationTopicGroup.objects.filter(deleted_at=None)
            serializer = NotificationTopicGroupSerializer(queryset, many=True)
            count = queryset.count()//StandardPagination.page_size
            return response_data(data={
                'numberPages': count,
                'list': serializer.data
            })
        except:
            return response_data(message='Lỗi truy vấn', status=4)
    
    def get_pin_noti(self, email, love=False):
        queryset = Notification.objects.filter(deleted_at=None,email=email, pin__isnull=False)
        if love:
            queryset = queryset.filter(love__isnull=False)
        serializer = NotificationSerializer(queryset, many=True)
        return serializer.data
    
    def get_noti(self, request):
        try:
            email = get_email_from_token(request)

            queryset = Notification.objects.filter(deleted_at=None, email=email, pin__isnull=True).exclude(topic_type="other")
            list_pin = self.get_pin_noti(email)
            read_all_active = False
            delete_noti_read_active = False
            if 'topicType' in request.GET:
                if request.GET["topicType"] != 'all':
                    topic_type = request.GET["topicType"]
                    queryset = Notification.objects.filter(deleted_at=None, email=email, topic_type=topic_type, pin__isnull=True)
                    list_pin = []
                if request.GET["topicType"] == 'love':
                    list_pin = self.get_pin_noti(email, love=True)
                    queryset = Notification.objects.filter(deleted_at=None, email=email, love__isnull=False, pin__isnull=True)

            paginator = StandardPagination()
            queryset = queryset.order_by('-received_at')
            read_all_active = bool(queryset.filter(is_readed=0).count())
            delete_noti_read_active = bool(queryset.filter(is_readed=1).count())
            count = queryset.count()//StandardPagination.page_size
            result = paginator.paginate_queryset(queryset, request)
            serializer = NotificationSerializer(result, many=True)
            list_noti = serializer.data
            return response_data(data={
                'numberPages': count,
                'listPin': list_pin,
                "read_all_btn": read_all_active,
                "delete_noti_read_btn": delete_noti_read_active,
                'list': list_noti
            })
        except:
            return response_data(status=4, message="Lỗi truy vấn")

    def do_action(self, request):
        try:
            action = ['read', 'read_all', 'delete', 'delete_all', 'love', 'restore']
            email = get_email_from_token(request)
            if 'action' not in request.data:
                return response_data(message='Phải truyền action', status=5)
            
            if request.data['action'] not in action:
                return response_data(message='Action không tồn tại', status=5)
            
            if request.data['action'] == 'read_all':
                if self.read_all(email):
                    return response_data(message='Cập nhật thành công', status=5)
            
            if request.data['action'] == 'delete_all':
                if self.delete_all(email):
                    return response_data(message='Xoá thành công', status=5)
                
            if request.data['action'] == 'restore':
                if self.restore_all(email):
                    return response_data(message='Cập nhật thành công', status=5)
                
            if 'id' not in request.data:
                return response_data(message='Phải truyền id', status=5)
            id = request.data['id']
            if id is None or len(id) <= 0:
                return response_data(message='Dữ liệu id sai hoặc không có giá trị', status=5)
            if request.data['action'] == 'read':
                for item in id:
                    if not self.post_read(item):
                        return response_data(message='lỗi hệ thống', status=4)
            elif request.data['action'] == 'delete':
                for item in id:
                    if not self.post_delete(item):
                        return response_data(message='lỗi hệ thống', status=4)
            elif request.data['action'] == 'love':
                for item in id:
                    if not self.post_love(item):
                        return response_data(message='lỗi hệ thống', status=4)
            return response_data(message='cập nhật thành công', status=1)
        except:
            return response_data(message='Lỗi truy vấn', status=4)
        
    def post_love(self, id):
        try:
            queryset = Notification.objects.get(id=id)
            serializer = NotificationSerializer(queryset)
            data = datetime.now()
            if serializer.data['isLove'] == 1:
                data = None
            queryset.love = data
            queryset.save()
            return response_data(message='Cập nhật thành công', status=1)
        except:
            return False
    
    def read_all(self, email):
        try:
            queryset = Notification.objects.filter(email=email)
            queryset.update(is_readed=1)
            return response_data(message='Cập nhật thành công', status=1)
        except:
            return False
    
    def delete_all(self, email):
        try:
            queryset = Notification.objects.filter(email=email, is_readed=1, pin__isnull=True)
            queryset.update(deleted_at=datetime.now())
            return response_data(message='Cập nhật thành công', status=1)
        except:
            return False
        
    def restore_all(self, email):
        try:
            queryset = Notification.objects.filter(email=email)
            queryset.update(deleted_at=None, is_readed=0)
            return response_data(message='Cập nhật thành công', status=1)
        except:
            return False
            
    def post_read(self, id):
        try:
            queryset = Notification.objects.get(id=id)
            queryset.is_readed = 1
            queryset.save()
            return response_data(message='Cập nhật thành công', status=1)
        except:
            return False
    
    def post_delete(self, id):
        try:
            queryset = Notification.objects.get(id=id, pin__isnull=True)
            queryset.deleted_at = datetime.now()
            queryset.save()
            return response_data(message='delete thành công', status=1)
        except:
            return False
    
    def send_noti_feedback(self, request):
        data = request.data
        serializer = NotificationValidator(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=serializer.errors)
        data = {
            "to": "fWvuDv0GS-Ce5Ngaze-REP:APA91bE7NP0f3WBGrA3S4ER6tve-x7WeesQRBRj8EdkWZUK6hspMN-xISLfAtt90iA3wIUI0JkBiaiLrZS8iQOpvc8B_UtONAhPQtNkjxmIf1Wm_PtippI8rWDOo9ZcmBq-v921hsUKy",
            "notification": {
                "title": "Liên Hệ Góp Ý",
                "body": "Đã gửi liên hệ góp ý thành công",
                "color":"#ff0000",
                "sound": "default"
            },
            "data": {
                "story_id": "story_12345"
            }
        }
        return response_data()
    
    def post_send_noti(self, request):
        try:
            postData = request.data
            topic = postData.get("topic", '')
            user_id = postData.get("userId", None)
            email = postData.get("email", None)
            device_token = postData.get("deviceToken", None)
            time_checkin = postData.get("timeCheckin", '')
            date_checkin = postData.get("dateCheckin", '')

            if (topic == '' ):
                return response_data(message='Topic không được rỗng', status=5)

            if (topic == 'checkin_ok' and (time_checkin == '' or date_checkin == '')):
                return response_data(message='Date, Time Checkin không được rỗng', status=5)

            if (NotificationTopic.objects.filter(topic_type=topic).exists()):
                topic_object = NotificationTopic.objects.get(topic_type=topic)
            else:
                return response_data(message='Không tìm thấy topic', status=1)
            
            str_center_app = topic_object.content_short
            str_popup = topic_object.content
            str_app = topic_object.content_long

            if(time_checkin):
                str_center_app = str_center_app.replace("[time]", time_checkin)
                str_popup = str_popup.replace("[time]", time_checkin)
                str_app = str_app.replace("[time]", str_app)

            if(date_checkin):
                str_center_app = str_center_app.replace("[date]", date_checkin)
                str_popup = str_popup.replace("[date]", date_checkin)
                str_app = str_app.replace("[date]", date_checkin)           

            notification_obj = Notification()
            notification_obj.topic_type = topic_object.topic_type
            notification_obj.user_id = user_id
            notification_obj.email = email
            notification_obj.gateway_id = ""
            notification_obj.title = topic_object.title_noti
            notification_obj.content_center_app = str_center_app
            notification_obj.content_popup = str_popup
            notification_obj.content_app = str_app
            notification_obj.url = topic_object.url            
            notification_obj.result_call_api = None
            notification_obj.process_status = "publish"
            notification_obj.created_at = datetime.now()
            notification_obj.direction = "popup"
            notification_obj.is_readed = 0
            notification_obj.is_fake = 0
            
            
            

            data = {
                'to' : device_token,
                'notification': {
                    "title": notification_obj.title,
                    "body": notification_obj.content_center_app,
                    "mutable_content": True,
                    "sound": "default",
                },
                "data": {
                    "url": "",
                    "direction": notification_obj.direction,
                    "title": notification_obj.title,
                    "body": notification_obj.content_popup,
                    "buttonOk": 'Xem chi tiết',
                    "buttonCancel": 'Đóng',
                }
            }

            result_fcm = FCMApi.sent_notification(data)
            if(result_fcm["success"] == 1):
                notification_obj.gateway_id = result_fcm["multicast_id"]
                notification_obj.is_send = 1
                notification_obj.updated_at = datetime.now()
            notification_obj.save()
            return response_data(data=result_fcm)
            # return response_data(message='delete thành công', status=1)
        except Exception as e:
            print("post_send_noti >> {} \n \n".format(e))
            return response_data(message='lỗi server', status=4)

    def test_call_pr(self, request):
        try:
            result = FCMApi.test_call_url_pr()
            print(result)
            # return response_data(status = result['statusCode'], message = result['message'], data = result['data'])
            return response_data(data=result)
        except Exception as e:
            print("test_call_pr >> {} \n \n" . format(e))
            return response_data(message='lỗi server test_call_pr', status=4)

    def test_call_pr_noproxy(self, request):
        try:
            result = FCMApi.test_call_url_pr_noproxy()
            print(result)
            # return response_data(status = result['statusCode'], message = result['message'], data = result['data'])
            return response_data(data=result)
        except Exception as e:
            print("test_call_pr >> {} \n \n" . format(e))
            return response_data(message='lỗi server test_call_pr', status=4)

@api_view(['POST'])
def sendNoti(request):
    postData = request.data
    topic = postData.get("topic", None)
    time_ = postData.get("time", None)
    date_ = postData.get("date", None)
    
    if (topic is None):
        return response_data(status=7, message="vui lòng nhập topic")

    title = 'Điểm danh thành công'
    content = 'Thiết bị đang sử dụng chưa đăng ký điểm danh cho tài khoản email đang đăng nhập ứng dụng. Vui lòng mở ứng dụng trên thiết bị [tên_thiết_bị_đăng_ký_tài_khoản] hoặc liên hệ với Admin chi nhánh để yêu cầu chuyển đổi.'   
    if(project_settings.ENV_APP == 'local'):
        authUserSession = {
            "clientId": "My_PT",
            "grantId": 5,
            "userId": 400,
            "email": "ThanhNPT@fpt.com.vn",
            "fullName": "Tran To Phong",
            "deviceId": "CAPTIAN-MARVEL-123456-789-999",
            "deviceName": "Captain marvel 123456",
            "deviceToken": "eoiffDTXT9mUIEjoU-3DpJ:APA91bEbAPdocK4SGOPcFze0scqpAoq7WtzQpqpdxxBWYyf982AH0UESi6zLq2cuR5a0nMuEkM2LA3xRUUKvEya7ZrqXPLcNZcW0ykusQrnxOi1aVHfuE_hgr7hMzntRmWrTxoo_pvgZ",
            "devicePlatform": "ANDROID",
            "deviceInfo": None,
            "isTinPncEmployee": 1,
            "userRoles": [
                "checkin",
                "tracking-tool",
                "games"
            ]
        }
    else:
        authUserSession = getUserAuthSessionData(request.headers.get("Authorization"))
    emp_email = authUserSession['email']
    emp_id = authUserSession['userId']

    topic_object = NotificationTopic.objects.get(topic_type=topic)

    str_center_app = topic_object.content_short
    str_popup = topic_object.content
    str_app = topic_object.content_long
    
    if(time_):
        str_center_app = str_center_app.replace("[time]", time_)
        str_popup = str_popup.replace("[time]", time_)
        str_app = str_app.replace("[time]", str_app)

    if(date_):
        str_center_app = str_center_app.replace("[date]", date_)
        str_popup = str_popup.replace("[date]", date_)
        str_app = str_app.replace("[date]", date_)

    notification_data = {
        "id": 1000,
        "topic_type": topic_object.topic_type,
        "user_id": emp_id,        
        "email": emp_email,
        "gateway_id": "",
        "title": topic_object.title_noti,
        "content_center_app": str_center_app,
        "content_popup": topic_object.content,
        "content_app": topic_object.content_long,
        "direction": topic_object.direction,
        "url": topic_object.url, 
        "result_call_api": None,
        "process_status": "publish",        
        # "created_at": datetime.now()
    }
    
    data = {
        'to' : authUserSession['deviceToken'],
        'notification': {
            "title": notification_data["title"],
            "body": notification_data["content_center_app"],
            "mutable_content": True,
            "sound": "default",
        },
        "data": {
            "url": "",
            "direction": "inapp",
            "title": notification_data["title"],
            "body": notification_data["content_popup"],
            "buttonOk": 'Xem chi tiết',
            "buttonCancel": 'Đóng',
        }
    }

    result_fcm = FCMApi.sent_notification(data)
    # print(result_fcm)
    if(result_fcm["success"] == 1):
        # notification_data["gateway_id"] = result_fcm["multicast_id"]
        notification_data["is_send"] = 1
        # notification_data["updated_at"] = datetime.now()

    # notification_object = Notification.objects.create(notification_data)
    # p, created = Notification.objects.get_or_create(notification_data)
    # notification_object.save()
    return response_data(data=result_fcm)

@api_view(['GET'])
def getNotisHome(request):
    
    post_data = request.data
    topic_type = post_data.get("topicType", 'all')
    print(1)
    #Get stock info from database
    if(project_settings.ENV_APP == 'local'):
        authUserSession = {
            "clientId": "My_PT",
            "grantId": 5,
            "userId": 3,
            "email": "ThanhNPT@fpt.com.vn",
            "fullName": "Tran To Phong",
            "deviceId": "CAPTIAN-MARVEL-123456-789-999",
            "deviceName": "Captain marvel 123456",
            "deviceToken": "eoiffDTXT9mUIEjoU-3DpJ:APA91bEbAPdocK4SGOPcFze0scqpAoq7WtzQpqpdxxBWYyf982AH0UESi6zLq2cuR5a0nMuEkM2LA3xRUUKvEya7ZrqXPLcNZcW0ykusQrnxOi1aVHfuE_hgr7hMzntRmWrTxoo_pvgZ",
            "devicePlatform": "ANDROID",
            "deviceInfo": None,
            "isTinPncEmployee": 1,
            "userRoles": [
                "checkin",
                "tracking-tool",
                "games"
            ]
        }
    else:
 
        authUserSession = getUserAuthSessionData(request.headers.get("Authorization"))
        print(authUserSession)

    email = authUserSession['email']
    emp_id = authUserSession['userId']
    
    
    query_group_topic = NotificationTopicGroup.objects.all()
    serializer_group_topic = NotificationTopicGroupSerializer(query_group_topic, many=True)
    list_topic = serializer_group_topic.data

    queryset = Notification.objects.all().filter(user_id=emp_id).filter(process_status='publish')
    if(topic_type != 'all'):
        queryset.filter(topic_type=topic_type)

    count = queryset.count()
    
    total_new = queryset.filter(is_readed=0).count()
    
    page = request.GET.get('page', 1)
    paginator = StandardPagination()
    result = paginator.paginate_queryset(queryset, request)    
    serializer = NotificationSerializer(result, many=True)
    data = {'numberPage': count//StandardPagination.page_size+1, 'numberNew': total_new, 'listTopic': list_topic, 'list': serializer.data}
    if(project_settings.ENV_APP == 'local'):
        data['sql_str'] = connection.queries
    resData = {'status':1, 'msg': 'Success', 'data':data}
    return Response(resData, status.HTTP_200_OK)

@api_view(["POST"])
def doTick(request):
    data = {'status':1, 'msg': 'Success'}
    return Response(data)

@api_view(["POST"])
def doBell(request):
    data = {'status':1, 'msg': 'Success'}
    return Response(data)

@api_view(["POST"])
def doAction(request):
    data = {'status':1, 'msg': 'Success'}
    return Response(data)

@api_view(["POST"])
def doAction(request):
    try:
        postData = request.data
        action = postData.get("action", None)
        id_item = postData.get("id_item", None)
        if(action != None and id_item != None):
            objectRow = Notification.objects.get(id=id_item)
            if(action == 'readed'):
                objectRow.is_readed = 1      
            elif(action == 'delete'):
                objectRow.process_status = 'deleted'
            elif(action == 'receive'):
                objectRow.received_at  = 'deleted'
            objectRow.save()
        return response_data()
    except:
        return response_data(status=4, message="Failed")
