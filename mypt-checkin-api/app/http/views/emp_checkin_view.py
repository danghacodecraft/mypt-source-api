# from rest_framework.views import APIView

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from ..models.emp_checkin import *
from ..serializers.emp_checkin_serializer import *
from ..serializers.account_management_serializer import *
from ..paginations.custom_pagination import *
from core.helpers.response import *
from core.helpers.utils import *
from core.helpers.utils_sql import *
from core.helpers.call_api import *
from core.helpers.global_variables import *

from http.entities import global_data
from core.helpers import auth_session_handler as authSessionHandler



class EmpCheckinView(ViewSet):
    def get_emp_info_checkin(self, request):

        fname = "get_emp_checkin"

        # data_token = global_data.authUserSessionData
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        emp_code = data_token.get("empCode", "")
        type_emp = data_token.get("empContractType", "")
        device_id = data_token.get('deviceId', '')
        # name = data_token.get("name", '')
        email = data_token.get("email", "")





        #   {
        #    "statusCode":1,
        #    "message":"Thành công",
        #    "data":{
        #       "stateWorking":"off",
        #       "shift":"",
        #       "blockName":"",
        #       "stateLate":0,
        #       "infoCheckin":"",
        #       "device":"",
        #       "accountMobinet":"",
        #       "date":"",
        #       "typeDate":"",
        #       "typeMonth":"",
        #       "strDate":"",
        #       "visibleCheckin":1,
        #       "functionResponse":0,
        #       "statusCheckin":1,
        #       "checkinTime":"11:39:10"
        #    }

        shift = ""
        state_working = "on"
        block_name = ""
        state_late = 0
        # info_checkin = "Bạn đã điểm danh đúng giờ"
        info_checkin = DICT_DATA_TEXT_INFO['ontime']
        device = ""
        account_MBN = ""
        str_full_date = ""
        thu = ""
        ngay = ""
        thang = ""
        visible_checkin = 1
        statusCheckin = 0
        checkin_time = ""
        function_response = 1
        code_shift = "O"
        ban_kinh = 0.0
        block_center = ""




        try:






            time_now = get_current_datetime()
            str_time_now = time_now.strftime('%Y-%m-%d_%H:%M:%S')
            __day = str_time_now.split("_")[0]
            time_hour = date_time_to_hour(time_now)

            thu, ngay, thang, str_full_date = convert_date(time_now)
            queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
            serializer = EmpCheckinSerializer(queryset, many=True)
            data_query = serializer.data
            if len(data_query) > 0:
                data_checkin = data_query[0]

                sheet_time = data_checkin['sheetTime']
                block_center = data_checkin['coordinateBlock']
                if block_center is None:
                    block_center = ""
                ban_kinh = data_checkin['blockDistance']
                if is_null_or_empty(ban_kinh):
                    ban_kinh = 0.0
                else:
                    ban_kinh = float(ban_kinh)

                shift = get_full_str_shift(sheet_time)
                code_shift = sheet_time
                if shift == "O":
                    state_working = "off"
                    shift = ""
                    block_name = ""
                    state_late = 0
                    info_checkin = "Hôm nay bạn không có lịch làm việc"
                    device = ""
                    account_MBN = ""
                    str_full_date = ""
                    thu = ""
                    ngay = ""
                    thang = ""
                    visible_checkin = 1
                    function_response = 0
                    statusCheckin = 0

                else:

                    block_name = data_checkin['blockName']

                    workday_factor = data_checkin['workdayFactor']
                    if workday_factor is None:
                        # info_checkin = "Bạn chưa được ghi nhận điểm danh"
                        info_checkin = DICT_DATA_TEXT_INFO['notok']
                        state_late = 99
                    else:
                        if workday_factor != 1:
                            # info_checkin = "Bạn đã điểm danh trễ"
                            info_checkin = DICT_DATA_TEXT_INFO['late']
                            state_late = 1

                    account_MBN = data_checkin['accountNameMBN']

                    queryset_account_mobinet = AccountManagement.objects.filter(emp_code=emp_code)
                    serializer_account_mobinet = AccountManagemenSerializer(queryset_account_mobinet, many=True)
                    data_query_account_mobinet = serializer_account_mobinet.data
                    if len(data_query_account_mobinet) > 0:
                        data_account = data_query_account_mobinet[0]
                        device = data_account.get('deviceName', '')

                    confirm_info = data_checkin['confirmInfo']
                    if confirm_info == 1:
                        visible_checkin = 0

                    checkin_success = data_checkin['checkinSuccess']
                    if checkin_success == "OK":
                        statusCheckin = 1
                        checkin_time = data_checkin['checkinTime']

            else:
                if type_emp == "new":
                    code_shift = "S"
                    shift = "Ca sáng"
                    state_working = "on"
                    queryset_account_mobinet = AccountManagement.objects.filter(emp_code=emp_code)
                    serializer_account_mobinet = AccountManagemenSerializer(queryset_account_mobinet, many=True)
                    data_query_account_mobinet = serializer_account_mobinet.data
                    if len(data_query_account_mobinet) > 0:
                        data_account = data_query_account_mobinet[0]
                        block_name = data_account.get('blockName', '')
                        block_center = data_account.get("coordinateWorking", "")
                        ban_kinh = data_account.get("workingRadius", 0.0)
                        state_late = 99
                        # info_checkin = "Bạn chưa được ghi nhận điểm danh"
                        info_checkin = DICT_DATA_TEXT_INFO['notok']
                        device = data_account.get('deviceName', '')
                        account_MBN = data_account.get('accountNameMBN', '')


                else:
                    state_working = "off"
                    shift = ""
                    block_name = ""
                    state_late = 0
                    info_checkin = "Hôm nay bạn không có lịch làm việc"
                    device = ""
                    account_MBN = ""
                    str_full_date = ""
                    thu = ""
                    ngay = ""
                    thang = ""
                    visible_checkin = 1
                    function_response = 0
                    statusCheckin = 1

            checkin_time_new = checkin_time
            if not is_null_or_empty(checkin_time):
                checkin_time_split = checkin_time.split(":")
                if len(checkin_time_split) == 3:
                    checkin_time_new = checkin_time_split[0] + " : " + checkin_time_split[1] + " : " + checkin_time_split[2]



            dict_data_output = {
                "stateWorking": state_working,
                "shift": shift,
                "blockName": block_name,
                "stateLate": state_late,
                "infoCheckin": info_checkin,
                "device": device,
                "accountMobinet": account_MBN,
                "date": str_full_date,
                "typeDate": thu,
                "typeMonth": thang,
                "strDate": str(ngay),
                "visibleCheckin": visible_checkin,
                "statusCheckin": statusCheckin,
                "checkinTime": checkin_time_new,
                "functionResponse": function_response,
                "empCode": emp_code,
                "codeShift": code_shift,
                "email": email,
                "blockCenter": block_center,
                "blockDistance": ban_kinh

            }

            # kiem tra thiet bi diem danh
            queryset_device = AccountManagement.objects.filter(emp_code=emp_code)
            serializer_device = AccountManagemenSerializer(queryset_device, many=True, fields=['deviceIdMypt'])
            list_data_device = serializer_device.data
            if len(list_data_device) > 0:
                info_device = list_data_device[0]
                device_id_init = info_device.get('deviceIdMypt', '')
                print("-------------------------------------CHECK DEVICE-------------------------")
                print(device_id_init)
                print(device_id)
                if device_id_init != device_id:
                    return response_data(data=dict_data_output, message=MESSAGE_API_SUCCESS, status=10)
            else:
                return response_data(data=dict_data_output, message=MESSAGE_API_SUCCESS, status=10)
            return response_data(data=dict_data_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("---------------------------------------------INFO CHECKIN -------------------------------------------")
            print("{} >> Error/Loi: {}".format(fname, ex))
            return  response_data(data={}, message=MESSAGE_API_FAILED, status=STATUS_CODE_ERROR_LOGIC)

    def report_checkin_on_month(self, request):
        fname = "report_checkin_on_month"

        # lay tu token
        # data_token = global_data.authUserSessionData
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        emp_code = data_token.get("empCode", "")
        user_email = data_token.get('email')
        # user_email = "phuongnam.quangbv@fpt.net"
        # emp_code = '00235901'

        # lay tu input
        # data_input = request.data
        data_input = request.GET
        month_input = str(data_input.get("month"))
        year_input = str(data_input.get('year'))


        try:

            token_auth = hr_auth()
            dict_info_user = get_employee_info(token_auth, user_email)

            str_start_contract = dict_info_user.get('startWorkingTime', '')
            if is_null_or_empty(str_start_contract):
                return response_data(data={}, message="Không có thông tin nhân viên",
                                     status=STATUS_CODE_ERROR_LOGIC)

            # str_start_contract = "25/04/2022"

            # checkin_date_first = list_data_checkin_date[0]['checkinDate']
            # checkin_date_first_date = convert_str_to_date(checkin_date_first)
            date_now = get_current_date()
            str_date_now = get_str_date_now_export()
            _date = str_date_now.split("/")[0]
            str_ngay_input = "{}/{}/{}".format(_date, month_input, year_input)
            ngay_input = convert_str_to_date(str_ngay_input)

            # queryset_device = AccountManagement.objects.filter(emp_code=emp_code)
            # serializer_device = AccountManagemenSerializer(queryset_device, many=True)
            # list_data_device = serializer_device.data
            # device_name = ""
            # if len(list_data_device) > 0:
            #     device_name = list_data_device[0]['deviceName']

            if ngay_input < date_now:
                queryset_first_workday = EmpCheckin.objects.filter(emp_code=emp_code).order_by('checkin_date')[0:1]
                serializer_first_workday = EmpCheckinSerializer(queryset_first_workday, many=True,
                                                                fields=['checkinDate'])
                list_data_checkin_date = serializer_first_workday.data
                if len(list_data_checkin_date) > 0:

                    # lay thong tin thiet bi thiet bi


                    checkin_date_first = list_data_checkin_date[0]['checkinDate']
                    checkin_date_first_date = convert_str_to_date(checkin_date_first)
                    # print("=================================check first date")
                    # print(str_start_contract)

                    if len(month_input) == 1:
                        month_input = "0" + month_input
                    time_now = get_current_datetime()
                    int_month = int(time_now.month)

                    int_month_input = int(month_input)
                    _date_input = str(year_input) + "-" + month_input
                    queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__startswith=_date_input).order_by('checkin_date')

                    serializer = EmpCheckinSerializer(queryset, many=True)
                    list_data = serializer.data
                    if len(list_data) > 0:
                        dict_info_output = info_history_checkin_on_month(list_data, emp_code,
                                                                         fname)

                        dict_info_output.update({
                            'firstWorkdate': str_start_contract
                        })

                        month_start_checkin = checkin_date_first.split("/")[1]
                        year_start_checkin = checkin_date_first.split("/")[2]

                        # if month_start_checkin == month_input:

                        if convert_str_to_date(checkin_date_first) == ngay_input:
                            # ngay ky hop dong ma ko di lam
                            str_start_contract = "01/{}/{}".format(month_start_checkin, year_start_checkin)
                            start_contract = convert_str_to_date(str_start_contract)
                            date_generated = [start_contract + timedelta(days=x) for x in
                                              range(0, (checkin_date_first_date - start_contract).days)]
                            # print(date_generated)
                            if len(date_generated) > 0:
                                list_event = dict_info_output.get('listEvent', [])
                                cnt_off = 0
                                # print(len(list_event))
                                for i_date in date_generated:
                                    checkin_date = convert_date_export(i_date)
                                    thu = get_type_date_fr_str_date(checkin_date, fname)
                                    if not is_null_or_empty(thu):
                                        thu = thu.title()
                                    str_date = thu + ", Ngày " + checkin_date
                                    list_event.append({
                                        "dateDetail": str_date,
                                        "date": checkin_date,
                                        "status": "off",
                                        "deviceName": '',
                                        "location": "",
                                        "timeCheckin": "",
                                        "numWorkday": 0.0
                                    })
                                    cnt_off = cnt_off + 1
                                list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                                dict_info_output['listEvent'] = list_event
                                dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off

                        # elif int(month_start_checkin) < int(month_input):
                        elif convert_str_to_date(checkin_date_first) < ngay_input:

                            # ngay ky hop dong ma ko di lam
                            # start_contract = convert_str_to_date(str_start_contract)
                            # % d / % m / % Y

                            str_start_contract = "01/{}/{}".format(month_input, year_input)

                            start_contract = convert_str_to_date(str_start_contract)
                            date_generated = [start_contract + timedelta(days=x) for x in
                                              range(0, (checkin_date_first_date - start_contract).days)]

                            if len(date_generated) > 0:
                                list_event = dict_info_output.get('listEvent', [])

                                cnt_off = 0

                                for i_date in date_generated:
                                    checkin_date = convert_date_export(i_date)
                                    thu = get_type_date_fr_str_date(checkin_date, fname)
                                    if not is_null_or_empty(thu):
                                        thu = thu.title()
                                    str_date = thu + ", Ngày " + checkin_date
                                    list_event.append({
                                        "dateDetail": str_date,
                                        "date": checkin_date,
                                        "status": "off",
                                        "deviceName": '',
                                        "location": "",
                                        "timeCheckin": "",
                                        "numWorkday": 0.0
                                    })
                                    cnt_off = cnt_off + 1
                                list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                                dict_info_output['listEvent'] = list_event
                                dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off



                        # =========================================

                        # dict_info_output = info_history_checkin_on_month(list_data, emp_code, device_name, fname)
                        # dict_info_output.update({
                        #     'firstWorkdate': checkin_date_first
                        # })

                        list_event = dict_info_output['listEvent']
                        # print(list_event)
                        list_event, cnt_off_2 = pre_process_list_info_checkin(list_event, month_input, year_input, True)
                        list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                        dict_info_output['listEvent'] = list_event
                        dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off_2

                        return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                             status=STATUS_CODE_SUCCESS)


                    else:
                        # khong co thong tin luc truc
                        list_info_checkin = info_history_month_not_start_checkin(str_start_contract, year_input, month_input)
                        if len(list_info_checkin) > 0:
                            dict_info_output = {
                                "countLate": 0,
                                "countOnTime": 0,
                                "countOff": len(list_info_checkin),
                                "countWorkday": 0,
                                'percentAbide': 100,
                                'percentNotAbide': 0,
                                "listEvent": list_info_checkin

                            }
                            dict_info_output.update(
                                {'firstWorkdate': str_start_contract})
                            return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                                 status=STATUS_CODE_SUCCESS)
                        else:
                            return response_data(data={'firstWorkdate': checkin_date_first},
                                                 message=MESSAGE_API_NO_DATA,
                                                 status=STATUS_CODE_NO_DATA)

                else:
                    # khong co thong tin diem danh
                    return response_data(data={}, message="Bạn chưa có thông tin điểm danh", status=STATUS_CODE_NO_DATA)

            elif ngay_input == date_now:
                queryset_first_workday = EmpCheckin.objects.filter(emp_code=emp_code).order_by('checkin_date')[0:1]
                serializer_first_workday = EmpCheckinSerializer(queryset_first_workday, many=True,
                                                                fields=['checkinDate'])
                list_data_checkin_date = serializer_first_workday.data
                if len(list_data_checkin_date) > 0:

                    # lay thong tin thiet bi thiet bi
                    queryset_device = AccountManagement.objects.filter(emp_code=emp_code)
                    serializer_device = AccountManagemenSerializer(queryset_device, many=True)
                    list_data_device = serializer_device.data
                    device_name = ""
                    if len(list_data_device) > 0:
                        device_name = list_data_device[0]['deviceName']

                    checkin_date_first = list_data_checkin_date[0]['checkinDate']
                    checkin_date_first_date = convert_str_to_date(checkin_date_first)
                    # print("=================================check first date")
                    # print(str_start_contract)

                    if len(month_input) == 1:
                        month_input = "0" + month_input
                    time_now = get_current_datetime()
                    int_month = int(time_now.month)

                    int_month_input = int(month_input)

                    from_date = str(year_input) + "-" + month_input + "-" + "01"
                    to_date = get_str_date_now_import_db()
                    queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__range=[from_date, to_date]).order_by('checkin_date')
                    # print(queryset.query)

                    serializer = EmpCheckinSerializer(queryset, many=True)
                    list_data = serializer.data
                    # list data la lay thong tin diem danh trong thang
                    if len(list_data) > 0:
                        # lay thong tin thiet bi thiet bi
                        dict_info_output = info_history_checkin_on_month_now(list_data, emp_code, fname)
                        dict_info_output.update({
                            'firstWorkdate': str_start_contract
                        })

                        # xu ly truong hop ngay dau tien di lam ma ko diem danh
                        month_start_checkin = checkin_date_first.split("/")[1]
                        year_start_checkin = checkin_date_first.split("/")[2]

                        # if month_start_checkin == month_input:
                        if convert_str_to_date(checkin_date_first) == ngay_input:
                            # ngay ky hop dong ma ko di lam
                            # start_contract = convert_str_to_date(str_start_contract)
                            # % d / % m / % Y
                            str_start_contract = "01/{}/{}".format(month_start_checkin, year_start_checkin)
                            start_contract = convert_str_to_date(str_start_contract)
                            date_generated = [start_contract + timedelta(days=x) for x in
                                              range(0, (checkin_date_first_date - start_contract).days)]
                            if len(date_generated) > 0:
                                list_event = dict_info_output.get('listEvent', [])

                                cnt_off = 0

                                for i_date in date_generated:
                                    checkin_date = convert_date_export(i_date)
                                    thu = get_type_date_fr_str_date(checkin_date, fname)
                                    if not is_null_or_empty(thu):
                                        thu = thu.title()
                                    str_date = thu + ", Ngày " + checkin_date
                                    list_event.append({
                                        "dateDetail": str_date,
                                        "date": checkin_date,
                                        "status": "off",
                                        "deviceName": '',
                                        "location": "",
                                        "timeCheckin": "",
                                        "numWorkday": 0.0
                                    })
                                    cnt_off = cnt_off + 1
                                list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                                dict_info_output['listEvent'] = list_event
                                dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off
                        # elif int(month_start_checkin) < int(month_input):
                        elif convert_str_to_date(checkin_date_first) < ngay_input:

                            # ngay ky hop dong ma ko di lam
                            # start_contract = convert_str_to_date(str_start_contract)
                            # % d / % m / % Y

                            str_start_contract = "01/{}/{}".format(month_input, year_input)

                            start_contract = convert_str_to_date(str_start_contract)
                            date_generated = [start_contract + timedelta(days=x) for x in
                                              range(0, (checkin_date_first_date - start_contract).days)]

                            if len(date_generated) > 0:
                                list_event = dict_info_output.get('listEvent', [])

                                cnt_off = 0

                                for i_date in date_generated:
                                    checkin_date = convert_date_export(i_date)
                                    thu = get_type_date_fr_str_date(checkin_date, fname)
                                    if not is_null_or_empty(thu):
                                        thu = thu.title()
                                    str_date = thu + ", Ngày " + checkin_date
                                    list_event.append({
                                        "dateDetail": str_date,
                                        "date": checkin_date,
                                        "status": "off",
                                        "deviceName": '',
                                        "location": "",
                                        "timeCheckin": "",
                                        "numWorkday": 0.0
                                    })
                                    cnt_off = cnt_off + 1
                                list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                                dict_info_output['listEvent'] = list_event
                                dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off

                        list_event = dict_info_output['listEvent']

                        list_event, cnt_off_2 = pre_process_list_info_checkin(list_event, month_input, year_input, False)
                        list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                        dict_info_output['listEvent'] = list_event
                        dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off_2
                        return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                             status=STATUS_CODE_SUCCESS)


                    else:
                        # khong co thong tin luc truc
                        list_info_checkin = info_history_month_not_start_checkin_month_now(str_start_contract, year_input,
                                                                                 month_input)
                        if len(list_info_checkin) > 0:
                            dict_info_output = {
                                "countLate": 0,
                                "countOnTime": 0,
                                "countOff": len(list_info_checkin),
                                "countWorkday": 0,
                                'percentAbide': 100,
                                'percentNotAbide': 0,
                                "listEvent": list_info_checkin

                            }
                            dict_info_output.update(
                                {'firstWorkdate': str_start_contract})
                            return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                                 status=STATUS_CODE_SUCCESS)
                        else:
                            return response_data(data={'firstWorkdate': str_start_contract},
                                                 message=MESSAGE_API_NO_DATA,
                                                 status=STATUS_CODE_NO_DATA)
                else:
                    return response_data(data={}, message="Bạn chưa có thông tin điểm danh", status=STATUS_CODE_NO_DATA)





        except Exception as ex:
            print("{} >> Error/Loi: {} \n \n".format(fname, ex))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)


    def report_checkin_on_month_tmp(self, request):
        fname = "report_checkin_on_month"

        # lay tu token
        # data_token = global_data.authUserSessionData
        # emp_code = data_token.get("empCode", "")
        emp_code = '00240340'
        user_email = "phuongnam.duyenntk@fpt.net"

        # lay tu input
        data_input = request.data
        month_input = data_input.get("month")
        year_input = data_input.get('year')

        try:
            token_auth = hr_auth()
            dict_info_user = get_employee_info(token_auth, user_email)
            print("====================")
            print(dict_info_user)

            queryset_first_workday = EmpCheckin.objects.filter(emp_code=emp_code).order_by('checkin_date')[0:1]
            serializer_first_workday = EmpCheckinSerializer(queryset_first_workday, many=True, fields=['checkinDate'])
            list_data_checkin_date = serializer_first_workday.data
            if len(list_data_checkin_date) > 0:
                checkin_date_first = list_data_checkin_date[0]['checkinDate']
                print(checkin_date_first)
                checkin_date_first_date = convert_str_to_date(checkin_date_first)
                month_start_checkin = checkin_date_first.split("/")[2]

                # lay thong tin ve ngay ky hop dong
                str_start_contract = dict_info_user.get('startWorkingTime', '')
                if is_null_or_empty(str_start_contract):
                    return response_data(data={}, message="Không có thông tin nhân viên", status=STATUS_CODE_ERROR_LOGIC)
                start_contract = convert_str_to_date(str_start_contract)
                date_generated = [start_contract + timedelta(days=x) for x in range(0, (checkin_date_first_date - start_contract).days + 1)]
                list_str_date_tmp = []
                if len(date_generated) > 0:
                    for i_date in date_generated:
                        list_str_date_tmp.append(convert_date_export(i_date))
                print(date_generated)
                print(list_str_date_tmp)

                return response_data(data={}, status=STATUS_CODE_SUCCESS, message=MESSAGE_API_SUCCESS)
            else:
                return response_data(data={}, status=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA)


            # # lay ngay dau tien cham cong
            # queryset_first_workday = EmpCheckin.objects.filter(emp_code=emp_code).order_by('checkin_date')[0:1]
            # serializer_first_workday = EmpCheckinSerializer(queryset_first_workday, many=True, fields=['checkinDate'])
            # list_data_checkin_date = serializer_first_workday.data
            # if len(list_data_checkin_date) > 0:
            #     checkin_date_first = list_data_checkin_date[0]['checkinDate']
            #
            #     if len(month_input) == 1:
            #         month_input = "0" + month_input
            #     time_now = get_current_datetime()
            #     int_month = int(time_now.month)
            #
            #     int_month_input = int(month_input)
            #     if int_month_input < int_month:
            #         _date_input = str(year_input) + "-" + month_input
            #         queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__startswith=_date_input)
            #
            #         serializer = EmpCheckinSerializer(queryset, many=True)
            #         list_data = serializer.data
            #         if len(list_data) > 0:
            #             dict_info_output = info_history_checkin_on_month(list_data, emp_code, fname)
            #             dict_info_output.update({
            #                 'firstWorkdate': checkin_date_first
            #             })
            #             return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
            #                                  status=STATUS_CODE_SUCCESS)
            #
            #
            #         else:
            #             return response_data(data={'firstWorkdate': checkin_date_first}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            #
            #     elif int_month == int_month_input:
            #         from_date = str(year_input) + "-" + month_input + "-" + "01"
            #         to_date = get_str_date_now_import_db()
            #         queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__range=[from_date, to_date])
            #         # print(queryset.query)
            #
            #         serializer = EmpCheckinSerializer(queryset, many=True)
            #         list_data = serializer.data
            #         if len(list_data) > 0:
            #             # lay thong tin thiet bi thiet bi
            #             dict_info_output = info_history_checkin_on_month_now(list_data, emp_code, fname)
            #             dict_info_output.update({
            #                 'firstWorkdate': checkin_date_first
            #             })
            #             return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
            #                                  status=STATUS_CODE_SUCCESS)
            #
            #
            #         else:
            #             return response_data(data={'firstWorkdate': checkin_date_first}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            #
            #     else:
            #         return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            # else:
            #     return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)



        except Exception as ex:
            print("{} >> Error/Loi: {} \n \n".format(fname, ex))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)


    def get_info_checkin_from_emp_code(self, request):
        # api cho service ho_profile goi
        data_input = request.data
        emp_code = data_input.get("empCode")
        type_emp = data_input.get("typeEmp")
        try:
            device_id = ""
            block_name = ""
            coordinate_block = ""
            coordinate_office = ""
            queryset = AccountManagement.objects.filter(emp_code=emp_code)
            serializer = AccountManagemenSerializer(queryset, many=True)
            list_data = serializer.data

            if len(list_data) > 0:
                device_id = list_data[0]['deviceIdMypt']

            queryset_checkin = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=get_str_date_now_import_db())
            serializer_checkin = EmpCheckinSerializer(queryset_checkin, many=True)
            list_data_checkin = serializer_checkin.data
            if len(list_data_checkin) > 0:
                block_name = list_data_checkin[0]['blockName']
                coordinate_block = list_data_checkin[0]['coordinateBlock']
                coordinate_office = list_data_checkin[0]['coordinateOffice']
            else:
                if type_emp != "official":
                    block_name = list_data[0]['blockName']
                    coordinate_block = list_data[0]['coordinateWorking']
                    coordinate_office = list_data[0]['coordinateOffice']

            dict_data = {
                "deviceId": device_id,
                "blockName": block_name,
                "coordinateBlock": coordinate_block,
                "coordinateOffice": coordinate_office
            }
            return response_data(data=dict_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("=====================get_info_device=============")
            print(ex)
            return response_data(data={}, message=MESSAGE_API_FAILED, status=STATUS_CODE_ERROR_LOGIC)




