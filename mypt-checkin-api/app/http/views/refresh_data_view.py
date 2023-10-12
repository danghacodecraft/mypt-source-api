from ..serializers.emp_checkin_serializer import *
from ..serializers.account_management_serializer import *
from ...core.helpers.response import *
from ...core.helpers.utils import *

from rest_framework.viewsets import ViewSet
from ...http.entities import global_data
from ...core.helpers import auth_session_handler as authSessionHandler

class RefreshData(ViewSet):
    def refresh_data_checkin(self, request):
        # lay tu token chua co empcode
        # data_token = global_data.authUserSessionData
        # emp_code = data_token.get("empCode", "")

        # lay tu input

        data_input = request.data
        emp_code = data_input.get('empCode', "")

        # output tra ve
        status_api = 0
        msg_api = "Co lỗi trong quá trình xử lý"

        try:
            time_now = get_current_datetime()
            str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
            __day = str_time_now.split(" ")[0]
            time__ = str_time_now.split(" ")[1]

            check_in = "NOT OK"
            note = ""
            add_checkin = ""
            workday_factor = None
            workday_convert = None
            EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
                checkin_success=check_in,
                location=add_checkin, note=note, count_auto=0,
                count_response=0, workday_factor=workday_factor, workday_convert=workday_convert)
            status_api = 1
            msg_api = "Thành công"
            # serializer = EmpCheckinSerializer(queryset, many=True)
            # data_query = serializer.data

        except Exception as e:
            print(e)

        return response_data(data={}, status=status_api, message=msg_api)

    def refresh_data_device(self, request):
        # lay tu token chua co empcode
        data_token = global_data.authUserSessionData
        emp_code = data_token.get("empCode", "")

        # lay tu input
        data_input = request.data
        emp_code = data_input.get('empCode', "")

        # output tra ve
        status_api = 0
        msg_api = "Co lỗi trong quá trình xử lý"

        try:

            AccountManagement.objects.filter(emp_code=emp_code).update(device_id_mypt=None, device_name=None)
            status_api = 1
            msg_api = "Thành công"
            # serializer = EmpCheckinSerializer(queryset, many=True)
            # data_query = serializer.data

        except Exception as e:
            print(e)

        return response_data(data={}, status=status_api, message=msg_api)