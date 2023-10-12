# from rest_framework.views import APIView

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from ..models.emp_checkin import *
from ..serializers.emp_checkin_serializer import *
from ..serializers.send_email_serializer import *
from ..serializers.account_management_serializer import *
from ..serializers.response_content_serializer import *
from ..paginations.custom_pagination import *
from core.helpers.response import *
from core.helpers.utils import *
from core.helpers.utils_sql import *
from core.helpers.call_api import *
from core.helpers.global_variables import *

from http.entities import global_data
from ..serializers.emp_response_serializer import *

from django.template.loader import get_template
from core.helpers.mail import *
import threading

from core.helpers import auth_session_handler as authSessionHandler
class HandleMail(threading.Thread):

    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_email_fpt(subject=self.subject, message=self.message, recipient_list=self.recipient_list)
        # return response_data()

class AddInfoCheckinView(ViewSet):

    def provide_info_device(self, request):
        # lay tu token, empcode chua co
        # data_token = global_data.authUserSessionData
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        emp_code = data_token.get("empCode", "")
        device_id = data_token.get("deviceId", "")
        device_name = data_token.get("deviceName", "")
        email = data_token.get("email", "")
        device_token = data_token.get('deviceToken', '')

        # ===============================================

        # device_id = "a6c88f1709f4367cd"
        # # device_name = "SAM SUNG"
        # # device_model = "GALAXY"
        # emp_code = "00203374"

        status_api = 0
        msg = ""
        try:
            AccountManagement.objects.filter(emp_code=emp_code).update(device_token=device_token)

            queryset_device = AccountManagement.objects.filter(device_id_mypt=device_id)
            serializer_device = AccountManagemenSerializer(queryset_device, many=True)
            data_device = serializer_device.data

            device_input = device_name
            if len(data_device) > 0:
                emp_code_init = data_device[0]['code']
                if emp_code_init != emp_code:
                    msg = "Thiết bị {} đã được ghi nhận đăng ký điểm danh cho tài khoản email khác " \
                          "thành công. Xin cảm ơn!".format(device_input)
                    return response_data(data={}, status=STATUS_CODE_FAILED, message=msg)
                else:
                    status_api = 1
                    msg = ""
                    return response_data(data={}, status=STATUS_CODE_SUCCESS, message=msg)
            else:
                queryset = AccountManagement.objects.filter(emp_code=emp_code)
                serializer = AccountManagemenSerializer(queryset, many=True)
                data_query = serializer.data
                account_class = AccountManagement()

                if len(data_query) == 0:

                    account_class.emp_code = emp_code
                    account_class.device_id_mypt = device_id
                    account_class.device_name = device_name
                    # account_class.device_model = device_model
                    account_class.save()
                    status_api = 1
                    msg = "Thiết bị {} đã được ghi nhận đăng ký điểm danh cho tài khoản email {} " \
                          "thành công. Xin cảm ơn!".format(device_input, email)
                    return response_data(data={}, status=STATUS_CODE_SUCCESS, message=msg)
                else:
                    device_id_init = data_query[0]['deviceIdMypt']
                    device_name_init = data_query[0]['deviceName']
                    if not is_null_or_empty(device_id_init):
                        if device_id_init != device_id:
                            msg = "Thiết bị đang sử dụng chưa đăng ký điểm danh cho tài khoản email {} đang đăng nhập ứng dụng. " \
                                  "Vui lòng mở ứng dụng trên thiết bị {} hoặc liên hệ với Admin chi nhánh để yêu cầu chuyển đổi".format(
                                email, device_name_init)
                            return response_data(data={}, status=STATUS_CODE_FAILED, message=msg)
                        else:
                            msg = ""
                            status_api = 1
                            return response_data(data={}, status=STATUS_CODE_SUCCESS, message=msg)
                    else:
                        AccountManagement.objects.filter(emp_code=emp_code).update(device_id_mypt=device_id,
                                                                                   device_name=device_name)
                        status_api = 1
                        msg = "Thiết bị {} đã được ghi nhận đăng ký điểm danh cho tài khoản email {} " \
                              "thành công. Xin cảm ơn!".format(device_input, email)

                        return response_data(data={}, status=STATUS_CODE_SUCCESS, message=msg)
        except Exception as e:
            print("provice_info_device >> {} \n \n".format(e))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)


    def send_response(self, request):
        fname = "send_response"
        # lay tu token
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        emp_code = data_token.get("empCode", "")
        user_name = data_token.get('fullName', '')
        user_email = data_token.get('email', '')
        parent_depart = data_token.get('parentDepart')
        device_id = data_token.get('deviceId', '')

        # emp_code = '00008594'
        # user_name = 'nguyễn thế kiệt'
        # user_email = 'duyen@fpt'
        # parent_depart = 'PNCV5'
        # # coordinate = '158.7,1885.5'
        # device_id = 'fbvgfd'


        # lay tu input
        data_input = request.data
        response_content = data_input.get("content", "")
        response_id = data_input.get("id", "")
        app_version = data_input.get('versionApp')
        coordinate = data_input.get('coordinate', '')

        status_api = 0
        msg = "Có lỗi trong quá trình xử lý"
        content = ""

        if is_null_or_empty(response_id):
            return response_data(data={}, message="Không có response id", status=STATUS_CODE_INVALID_INPUT)

        try:

            time_now = get_current_datetime()
            str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')

            queryset = EmpResponse.objects.filter(emp_code=emp_code, update_time=str_time_now).order_by('-update_time')[0:1]
            serializer = EmpResponseSerializer(queryset, many=True, fields=['updateTime'])
            list_update = serializer.data
            if len(list_update) > 0:
                str_t_update = list_update[0]['updateTime']
                time_update = convert_str_to_datetime(str_t_update, fname)
                _second = compute_interval(time_update, time_now)
                if _second < 30:
                    return response_data(data={}, message="Input không hợp lệ", status=STATUS_CODE_ERROR_LOGIC)





            status_api = 1
            msg = "Bạn đã phản hồi thành công"
            content = "Cám ơn bạn đã dành thời gian phản hồi !\n Chúc bạn một ngày làm việc tốt lành"
            data = {
                "title": msg,
                "content": content

            }

            queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=get_str_date_now_import_db())
            serializer = EmpCheckinSerializer(queryset, many=True, fields=['teamName', 'sheetTime', 'id'])
            list_data = serializer.data
            ca = ""
            checkin_id = None
            if len(list_data) > 0:
                ca_ = list_data[0]['sheetTime']
                if ca_ == "S":
                    ca = "Ca Sáng"
                elif ca_ == "C":
                    ca = "Ca Chiều"
                elif ca_ == "O":
                    ca = "Ca Off"
                checkin_id = list_data[0]['id']


            # emp_response = EmpResponse()
            # emp_response.update_time = str_time_now
            # emp_response.emp_code = emp_code
            # emp_response.response = response_content
            # emp_response.response_id = response_id
            # emp_response.coordinate = coordinate
            # emp_response.checkin_id = checkin_id
            # save_response = emp_response.save()
            insert_response(str_time_now,emp_code,response_content,response_id,coordinate,checkin_id,device_id)

            queryset_content = ResponseContent.objects.filter(id=response_id)
            serializer_content = ResponseContentSerializer(queryset_content, many=True)
            data_content = serializer_content.data
            content_email = ''
            if len(data_content) > 0:
                content_email = data_content[0]['contentResponse']




            # goi api gui email
            subject = parent_depart + "_" + user_name

            khac = ""
            if int(response_id) == 12:
                khac = response_content



            content_email_1 = "<p style=\'color:#ED7D31;\'> <i> Lưu ý: Đây là email tự động từ hệ thống, vui lòng không reply lại nội dung email này. (This is an automatic email sent from the system, please do not reply back to this email content)</i></p><br>" \
                            "Anh/Chị thân mến,<br> <br>"

            content_email_1 = content_email_1 + "My PT vừa nhận được phản hồi về điểm danh từ email {} thuộc chi nhánh {}, phản hồi chi tiết như sau:<br>".format(user_email, parent_depart)
            content_email_1 = content_email_1 + "<ul style=\"list-style-type: disc;\">" + \
                              "<li><strong><span style=\"color:black;\">Chi tiết phản hồi:</span></strong>&nbsp;{}</li> ".format(content_email) + \
    "<li><strong><span style=\"color:black;\">Nội dung chi tiết:</span></strong>&nbsp;{}</li>".format(khac) + \
    "<li><strong><span style=\"color:black;\">Tọa độ phản hồi:</span></strong> &nbsp;{}</li>".format(coordinate) + \
    "<li><strong><span style=\"color:black;\">Thời gian ghi nhận phản hồi:</span></strong>&nbsp;{}</li>".format(get_str_datetime_now_export())+ \
    "<li><strong><span style=\"color:black;\">Lịch trực:&nbsp;</span></strong>&nbsp;{}</li>".format(ca) + \
    "<li><strong><span style=\"color:black;\">Thiết bị phản hồi điểm danh:</span></strong>&nbsp;{} </li>".format(device_id) + \
    "<li><strong><span style=\"color:black;\">Version ứng dụng:</span></strong>&nbsp;{}</li></ul>".format(app_version)
            content_email_1 = content_email_1 + "Anh/Chị vui lòng tiếp nhận và tiếp tục xử lý phản hồi theo quy trình. " \
                                                "<br> <br> My PT cảm ơn Anh/Chị. <br>Trân trọng, <br>My PT"


            subject = "[{}] - {} vừa phản hồi điểm danh trên My PT".format(parent_depart, user_name)
            recipient_list = ["ftel.pnc.pdx@fpt.net", ]
            query_email = SendEmail.objects.all()
            serializer_email = SendEmailSerializer(query_email, many=True)
            list_email = serializer_email.data
            recipient_list = []
            if len(list_email) > 0:
                for k in list_email:
                    recipient_list.append(k['email'])

            HandleMail(subject=subject, message=content_email_1, recipient_list=recipient_list).start()

            # list_email_nhan = ['ftel.pnc.pdx@fpt.net']
            # params = {
            #     "subject": subject,
            #     "content": content_email,
            #     "listReceive": list_email_nhan,
            #
            # }
            # call_api_send_email(params)


            return response_data(data=data, status=STATUS_CODE_SUCCESS, message=MESSAGE_API_SUCCESS)

        except Exception as e:
            print("send_response >>  Error/ loi >> {} ".format(e))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)