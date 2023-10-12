# from rest_framework.views import APIView
import json

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from ..models.emp_checkin import *
from ..serializers.emp_checkin_serializer import *
from ..serializers.account_management_serializer import *
from ..paginations.custom_pagination import *
from ...core.helpers.response import *
from ...core.helpers.utils import *
from ...core.helpers.utils_sql import *
from ...core.helpers.call_api import *
from ...core.helpers.global_variables import *

from ...http.entities import global_data

from ..serializers.emp_checkin_history_serializer import *
from django.db import transaction
from django.conf import settings as project_settings
import redis
from ...core.helpers import auth_session_handler as authSessionHandler

class UpdateInfoCheckinView(ViewSet):
    def confirm_info_checkin(self, request):
        fname = 'confirm_info_checkin'
        # lay tu token
        # data_token = global_data.authUserSessionData
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        emp_code = data_token.get("empCode", "")
        user_id = data_token.get('userId', '')
        try:
            time_now = get_current_datetime()
            str_time_now = time_now.strftime('%Y-%m-%d_%H:%M:%S')
            __day = str_time_now.split("_")[0]
            EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(confirm=1)

            print("=======================AN TAB DIEM DANH=====================")
            call_api_disable_checkin(user_id, fname)



            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("---------------------confirm_info_checkin-------------------")
            print(ex)
            return response_data(data={}, message=MESSAGE_API_FAILED, status=STATUS_CODE_ERROR_LOGIC)


    def get_coordinate(self, request):
        # nhan vien moi thi ko co block diem danh
        headerAuthToken = request.headers.get("Authorization")

        # lay tu token
        # data_token = global_data.authUserSessionData
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        emp_code = data_token.get("empCode", "")
        _type_emp = data_token.get("empContractType", "")
        branch = data_token.get("branch", "")
        user_email = data_token.get('email')
        device_id = data_token.get('deviceId', '')
        device_name = data_token.get('deviceName', '')


        # emp_code = "00235901"
        # _type_emp = "official"
        # branch = "PNC"
        # user_email = "phuongnam.viennt1@fpt.net"
        # device_id = "D5C3D229-7C98-4F1E-971F-E1E519C7187F"
        # device_name = "Viễn 123"







        # print("???")
        # print(emp_code)
        # print(_type_emp)

        # ==================================================

        # lay tu input
        data_input = request.data
        coordinate = data_input.get('coordinate', "")
        type_checkin = data_input.get("type", "auto")



        if is_null_or_empty(coordinate):
            content_output = "Không lấy được tọa độ"
            return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
        try:



            query_account = AccountManagement.objects.filter(emp_code=emp_code)
            serializer_account = AccountManagemenSerializer(query_account, many=True)
            list_data_count = serializer_account.data
            if len(list_data_count) > 0:
                device_id_db = list_data_count[0]['deviceIdMypt']
                if device_id_db != device_id:
                    print("===================CHECK TOKEN LAY TOA DO==================")
                    # print(device_id_db)
                    # print(device_id)
                    txt_failed = "<p>Thiết bị đang sử dụng <strong>chưa đăng ký điểm danh</strong> cho tài khoản email đang đăng nhập ứng dụng.</p><br><p>Vui lòng mở ứng dụng trên thiết bị <strong> {} </strong> hoặc liên hệ với Admin chi nhánh để yêu cầu chuyển đổi.</p>".format(
                        list_data_count[0]['deviceName'])

                    return response_data(data={"detail": txt_failed}, status=10, message=MESSAGE_API_FAILED_CHECKIN)

            time_now = get_current_datetime()
            time_hour = date_time_to_hour(time_now)
            if time_hour < 5:
                return response_data(data="", status=11, message="Hệ thống chỉ thực hiện điểm danh hoặc thông qua phản hồi sau 5 giờ sáng. Bạn vui lòng mở lại App sau 5h để thực hiện điểm danh.\nXin cảm ơn!")


            str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
            __day = str_time_now.split(" ")[0]
            time__ = str_time_now.split(" ")[1]

            # ket noi redis
            # redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
            #                                   , port=project_settings.REDIS_PORT_CENTRALIZED
            #                                   , db=project_settings.REDIS_DATABASE_CENTRALIZED,
            #                                   password=project_settings.REDIS_PASSWORD_CENTRALIZED
            #                                   , decode_responses=True, charset="utf-8")
            # contract_redis = redisInstance.get("checkin-" + __day + "-" + emp_code)
            # if contract_redis is not None:
            #     # ton tai
            #     return response_data(status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED, data={})
            # redisInstance.set("checkin-" + __day + "-" + emp_code, 5, 2)






            success = " thành công"
            # _type_content_output = "Điểm danh tự động"
            if _type_emp == "official":
                # queryset = EmpCheckin.objects.all() cau query lay full data
                queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
                serializer = EmpCheckinSerializer(queryset, many=True)
                data_query = serializer.data

                if len(data_query) > 0:
                    data_checkin = data_query[0]
                    # print(data_checkin)

                    id_checkin = data_checkin['id']
                    emp_id = data_checkin['accountNameMBN']
                    res_time = time__
                    ca = data_checkin['sheetTime']
                    coordinate_office = data_checkin['coordinateOffice']
                    block_name = data_checkin['blockName']
                    block_distance = data_checkin['blockDistance']
                    coordinate_block = data_checkin['coordinateBlock']
                    team_name = data_checkin['teamName']
                    checkin_success = data_checkin['checkinSuccess']
                    history_coordiante = data_checkin['historyCoordinate']

                    if ca != "O":
                        if checkin_success != "OK":



                            reason_failed = ""
                            # add_checkin = ""

                            # kiem tra toa do
                            if not check_input_toa_do(coordinate_block):
                                content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(coordinate_block)

                                return response_data(data={"detail": content_output}, status=10, message=MESSAGE_API_FAILED_CHECKIN)

                            if not check_input_toa_do(coordinate_office):
                                content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                                    coordinate_office)

                                return response_data(data={"detail": content_output}, status=10,
                                                     message=MESSAGE_API_FAILED_CHECKIN)



                                # xu ly vi tri

                            dict_position = calculcate_distance_for_official_emp(emp_coordinate=coordinate,block_center=coordinate_block,block_distance=block_distance,office_center=coordinate_office,block_name=block_name)
                            status_position = dict_position["checkin"]
                            add_checkin = dict_position['location']


                            if status_position == "NOTOK":
                                # reason_failed = "VỊ TRÍ ĐIỂM DANH KHÔNG PHÙ HỢP"
                                # check_in = "NOT OK"
                                # status = 0
                                return response_data(data={"detail":"Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc"}, message= MESSAGE_API_FAILED_CHECKIN, status=STATUS_CODE_INVALID_INPUT)
                            else:
                                dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now, ca, add_checkin)
                                status = dict_data_workday['status']
                                check_in = dict_data_workday['check_in']



                                workday_convert = status
                                # if status < 0.7:
                                #     workday_convert = 0


                                EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
                                    checkin_success=check_in,
                                    workday_factor=status,
                                    workday_convert=workday_convert,
                                    checkin_time=res_time,
                                    location=add_checkin, device_name=device_name)
                                if type_checkin == "response":
                                    EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(count_auto=99)

                                # _type_content_output = _type_content_output + success
                                # status_checkin = 1
                                # status_api = 1
                                # content_output = _type_content_output + success

                                date_now = get_current_date()
                                str_time_now_new = date_now.strftime('%d/%m/%Y')
                                params = {
                                        "email": user_email,
                                        "title": "Điểm danh thành công",
                                        "body": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(res_time, str_time_now_new),
                                        "notificationLayout": "",
                                        "topic_type": "checkin",
                                        "notifyActionType": "go_to_screen",
                                        "notifyDataAction": "/check-in-history",
                                        "popupDetailActionType": "go_to_screen",
                                        "popupDetailDataAction": "/check-in-history",
                                        # "navigate": "/historyCheckIn"


                                }
                                print(params)
                                msg = call_api_noti_success_checkin(params)
                                # print("-----------------------BAN NOT -------------------------")
                                # print(msg)
                                return response_data(data={"detail": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(res_time, str_time_now_new)}, message=MESSAGE_API_SUCCESS_CHECKIN, status=STATUS_CODE_SUCCESS)


                        else:
                            content_output = "Bạn đã điểm danh"
                            return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
                    else:

                        # if not is_null_or_empty(history_coordiante):
                        #     list_history = eval(history_coordiante)
                        #     list_history.append({
                        #         'res_time': time__,
                        #         'coordinate': coordinate
                        #     })
                        # else:
                        #     list_history = [{
                        #         'res_time': time__,
                        #         'coordinate': coordinate
                        #     }]
                        # EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(history_coordinate=list_history)
                        save_db_shift_off_new(history_coordiante, res_time, coordinate, emp_code, __day, block_distance, coordinate_block, coordinate_office, block_name,team_name, str_time_now, ca, device_name)


                        content_output = "Hệ thống sẽ không ghi nhận điểm danh khi nhân viên không có lịch trực trong ngày. Mọi thắc mắc xin vui lòng liên hệ Admin chi nhánh"
                        return response_data(data={"detail": content_output}, status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED_CHECKIN)

                else:
                    content_output = "Hệ thống sẽ không ghi nhận điểm danh khi nhân viên không có lịch trực trong ngày. Mọi thắc mắc xin vui lòng liên hệ Admin chi nhánh"
                    return response_data(data={"detail": content_output}, status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED_CHECKIN)

            else:

                ca = "S"
                full_date = __day.split("-")
                _year = full_date[0]
                _month = full_date[1]
                _day = full_date[2]
                emp_checkin_class = EmpCheckin()
                # queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
                queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
                serializer = EmpCheckinSerializer(queryset, many=True)
                data_query = serializer.data

                note = ""

                ok_continue = True

                if len(data_query) == 0:
                    emp_checkin_class.emp_code = emp_code
                    # emp_checkin_class.MBN_account_name = emp_id
                    emp_checkin_class.checkin_date = __day
                    emp_checkin_class.checkin_day = _day
                    emp_checkin_class.checkin_month = _month
                    emp_checkin_class.checkin_year = _year
                    emp_checkin_class.sheet_time = ca
                    emp_checkin_save = emp_checkin_class.save()

                    queryset_info_checkin_condition = AccountManagement.objects.filter(emp_code=emp_code)
                    serializer_checkin_condition = AccountManagemenSerializer(queryset_info_checkin_condition,
                                                                              many=True)
                    data_query_checkin_condition = serializer_checkin_condition.data
                    if len(data_query_checkin_condition) == 0:
                        content_output = "Không tìm thấy thông tin về địa điểm điểm danh của bạn. Vui lòng liên hệ quản lý"
                        return response_data(data={"detail": content_output}, status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED_CHECKIN)
                    info_checkin = data_query_checkin_condition[0]

                    toa_do_van_phong = info_checkin['coordinateOffice']
                    toa_do_kho = info_checkin['coordinateWarehouse']
                    toa_do_lam_viec = info_checkin['coordinateWorking']
                    ban_kinh_lam_viec = info_checkin['workingRadius']
                    emp_id = info_checkin['accountNameMBN']
                    team_name = get_branch_fr_account_mobinet(emp_id)

                    if not check_input_toa_do(toa_do_van_phong):
                        content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                            toa_do_van_phong)

                        return response_data(data={"detail": content_output}, status=10,
                                             message=MESSAGE_API_FAILED_CHECKIN)

                    if not check_input_toa_do(toa_do_lam_viec):
                        content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                            toa_do_lam_viec)

                        return response_data(data={"detail": content_output}, status=10,
                                             message=MESSAGE_API_FAILED_CHECKIN)

                    if not check_input_toa_do(toa_do_kho):
                        content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                            toa_do_kho)

                        return response_data(data={"detail": content_output}, status=10,
                                             message=MESSAGE_API_FAILED_CHECKIN)


                    data_position = calculate_distance_for_new_emp(coor_emp=coordinate,
                                                                   toa_do_van_phong=toa_do_van_phong,
                                                                   toa_do_kho=toa_do_kho,
                                                                   toa_do_lam_viec=toa_do_lam_viec,
                                                                   str_ban_kinh_lam_viec=ban_kinh_lam_viec)
                    error_position = data_position.get('error')
                    if error_position == "ok":
                        return response_data(data={"detail": "Không tìm thấy thông tin về địa điểm điểm danh của bạn. Vui lòng liên hệ quản lý"}, status=STATUS_CODE_INVALID_INPUT,
                                             message=MESSAGE_API_FAILED_CHECKIN)


                    data_status_checkin = data_position.get("checkin", "NOT OK")

                    location = data_position.get("location", "")
                    if location == "BLOCK":
                        block_name = "BLOCK"
                    else:
                        block_name = ""
                    # if emp_id != "":
                    #     team_name = str(emp_id).split(".")[0]
                    if data_status_checkin == "OK":

                        data_workday = calculate_workday_factor(branch, str_time_now, ca, location)
                        workday_factor = data_workday.get('workday', 0)
                        # too_late = data_workday.get('too_late')
                        workdate_convert = workday_factor
                        # if workday_factor < 0.7:
                        #     workdate_convert =0

                        EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
                            MBN_account_name=emp_id, team_name=team_name,
                            block_name=block_name,
                            checkin_success=data_status_checkin,
                            workday_factor=workday_factor,
                            workday_convert=workdate_convert,
                            checkin_time=time__,
                            location=location, device_name=device_name)

                        if type_checkin == "response":
                            EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(count_auto=99)

                        # content_output = _type_content_output + success

                        date_now = get_current_date()
                        str_time_now_new = date_now.strftime('%d/%m/%Y')
                        params = {
                            "email": user_email,
                            "title": "Điểm danh thành công",
                            "body": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(time__,
                                                                                            str_time_now_new),
                            "notifyActionType": "go_to_screen",
                            "notifyDataAction": "/check-in-history",
                            "popupDetailActionType": "go_to_screen",
                            "popupDetailDataAction": "/check-in-history",
                            "topic_type": "checkin",

                        }
                        msg = call_api_noti_success_checkin(params)
                        print("-----------------------BAN NOT -------------------------")
                        print(msg)
                        return response_data(data={"detail": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(time__,
                                                                                            str_time_now_new)}, message=MESSAGE_API_SUCCESS_CHECKIN, status=STATUS_CODE_SUCCESS)
                    else:
                        return response_data(data={"detail": "Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc"},
                                             message= MESSAGE_API_FAILED_CHECKIN,
                                             status=STATUS_CODE_INVALID_INPUT)


                else:
                    note = data_query[0]['note']
                    checkin_success = data_query[0]['checkinSuccess']
                    toa_do_lam_viec = data_query[0]['coordinateBlock']
                    toa_do_van_phong = data_query[0]['coordinateOffice']
                    ca = data_query[0]['sheetTime']
                    toa_do_kho = "0, 0"
                    ban_kinh_lam_viec = data_query[0]['blockDistance']
                    emp_id = data_query[0]['accountNameMBN']
                    history_coordinate = data_query[0]['historyCoordinate']
                    block_name = data_query[0]['blockName']

                    team_name = get_branch_fr_account_mobinet(emp_id)
                    if checkin_success == "OK" and ca != "O":
                        content_output = "Bạn đã điểm danh"
                        return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)

                    if ca != "O":

                        if checkin_success != "OK":
                            reason_failed = ""
                            # add_checkin = ""

                            # xu ly vi tri

                            if is_null_or_empty(toa_do_van_phong) or is_null_or_empty(toa_do_lam_viec) or is_null_or_empty(ban_kinh_lam_viec):
                                queryset_info_checkin_condition = AccountManagement.objects.filter(emp_code=emp_code)
                                serializer_checkin_condition = AccountManagemenSerializer(
                                    queryset_info_checkin_condition,
                                    many=True)
                                data_query_checkin_condition = serializer_checkin_condition.data
                                if len(data_query_checkin_condition) == 0:
                                    content_output = "Thông tin của bạn chưa được cập nhật trên hệ thống quản lý nhân sự. Vui lòng liên hệ quản lý trực tiếp để được hỗ trợ.\nXin cảm ơn"
                                    return response_data(data={}, status=STATUS_CODE_INVALID_INPUT,
                                                         message=content_output)
                                info_checkin = data_query_checkin_condition[0]
                                toa_do_lam_viec = info_checkin['coordinateWorking']
                                toa_do_van_phong = info_checkin['coordinateOffice']
                                ban_kinh_lam_viec = info_checkin['workingRadius']
                                if is_null_or_empty(toa_do_van_phong) and is_null_or_empty(toa_do_lam_viec):
                                    return response_data(data={"detail": "Bạn chưa được khai báo thông tin điểm danh. Vui lòng liên hệ quản lý trực tiếp để được hỗ trợ.\nXin cảm ơn"}, status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED_CHECKIN)

                            if not check_input_toa_do(toa_do_van_phong):
                                content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                                    toa_do_van_phong)

                                return response_data(data={"detail": content_output}, status=10,
                                                     message=MESSAGE_API_FAILED_CHECKIN)

                            if not check_input_toa_do(toa_do_lam_viec):
                                content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                                    toa_do_lam_viec)

                                return response_data(data={"detail": content_output}, status=10,
                                                     message=MESSAGE_API_FAILED_CHECKIN)

                            if not check_input_toa_do(toa_do_kho):
                                content_output = "<p>Tọa độ điểm danh của bạn là: <span style=\"color: red;\"><strong>{}</strong></span>, tọa độ này không đúng định dạng;</p><br><p>Bạn vui lòng liên hệ Quản lý user cập nhật lại để tiếp tục thực hiện điểm danh.</p>".format(
                                    toa_do_kho)

                                return response_data(data={"detail": content_output}, status=10,
                                                     message=MESSAGE_API_FAILED_CHECKIN)








                            dict_position = calculcate_distance_for_official_emp(emp_coordinate=coordinate,block_center=toa_do_lam_viec,block_distance=ban_kinh_lam_viec,office_center=toa_do_van_phong,block_name=block_name)
                            error_position = dict_position.get('error')
                            if error_position == "ok":
                                print("{} ------------------------- loi tinh khoang cach")
                                return response_data(data={}, status=STATUS_CODE_INVALID_INPUT,
                                              message="Không tìm thấy thông tin về địa điểm điểm danh của bạn. Vui lòng liên hệ quản lý")


                            status_position = dict_position["checkin"]
                            add_checkin = dict_position['location']



                            if status_position == "NOTOK":
                                # reason_failed = "VỊ TRÍ ĐIỂM DANH KHÔNG PHÙ HỢP"
                                # check_in = "NOT OK"
                                # status = 0
                                return response_data(data={}, message="Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc", status=STATUS_CODE_INVALID_INPUT)
                            else:

                                dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now, ca, add_checkin)
                                status = dict_data_workday['status']
                                check_in = dict_data_workday['check_in']



                                workday_convert = status
                                # if status < 0.7:
                                #     workday_convert = 0


                                EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
                                    checkin_success=check_in,
                                    workday_factor=status,
                                    workday_convert=workday_convert,
                                    checkin_time=time__,
                                    location=add_checkin, device_name=device_name)
                                if type_checkin == "response":
                                    EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(count_auto=99)

                                # _type_content_output = _type_content_output + success
                                # status_checkin = 1
                                # status_api = 1
                                # content_output = _type_content_output + success



                                # ban noti
                                date_now = get_current_date()
                                str_time_now_new = date_now.strftime('%d/%m/%Y')
                                params = {
                                        "email": user_email,
                                        "title": "Điểm danh thành công",
                                        "body": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(time__, str_time_now_new),
                                        "topic_type": "checkin",
                                        "notifyActionType": "go_to_screen",
                                        "notifyDataAction": "/check-in-history",
                                        "popupDetailActionType": "go_to_screen",
                                        "popupDetailDataAction": "/check-in-history",
                                    # "navigate": "/historyCheckIn"
                                }
                                msg = call_api_noti_success_checkin(params)
                                print("-----------------------BAN NOT -------------------------")
                                print(msg)
                                return response_data(data={"detail": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(time__, str_time_now_new)}, message=MESSAGE_API_SUCCESS_CHECKIN, status=STATUS_CODE_SUCCESS)


                        else:
                            content_output = "Bạn đã điểm danh"
                            return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)

                    else:
                        res_time = time__
                        save_db_shift_off_new(history_coordinate, res_time, coordinate, emp_code, __day, ban_kinh_lam_viec, toa_do_lam_viec, toa_do_van_phong, block_name,team_name, str_time_now, ca, device_name)

                        content_output = "Hệ thống sẽ không ghi nhận điểm danh khi nhân viên không có lịch trực trong ngày. Mọi thắc mắc xin vui lòng liên hệ Admin chi nhánh"
                        return response_data(data={"detail": content_output}, status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED_CHECKIN)


            # insert_log_get_coordinate(str_time_now, type_checkin, coordinate, status_checkin, __day, emp_code) # luu log lich su

        except Exception as e:
            # transaction.rollback()
            print("---------------get_coordinate----------------------")
            print(e)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)


        # lay data
        # k = serializer.data
        # print(k[0]['id'])

        # data = {
        #     "contentNoti": content_output,
        # }


    # def get_coordinate(self, request):
    #     # nhan vien moi thi ko co block diem danh
    #     headerAuthToken = request.headers.get("Authorization")
    #
    #     # lay tu token
    #     data_token = global_data.authUserSessionData
    #     emp_code = data_token.get("empCode", "")
    #     _type_emp = data_token.get("empContractType", "")
    #     branch = data_token.get("branch", "")
    #     user_email = data_token.get('email')
    #
    #
    #
    #     # print("???")
    #     # print(emp_code)
    #     # print(_type_emp)
    #
    #     # ==================================================
    #
    #     # lay tu input
    #     data_input = request.data
    #     coordinate = data_input.get('coordinate', "")
    #     type_checkin = data_input.get("type", "auto")
    #
    #     content_output = "Điểm danh thất bại"
    #     status_api = 0
    #     count_auto = 0
    #     count_response = 0
    #     status_checkin = 0
    #     # too_late = 0
    #
    #     ok_send_noti = False
    #
    #     if is_null_or_empty(coordinate):
    #         content_output = "Không lấy được tọa độ"
    #         return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #     try:
    #
    #         time_now = get_current_datetime()
    #         str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
    #         __day = str_time_now.split(" ")[0]
    #         time__ = str_time_now.split(" ")[1]
    #
    #         if type_checkin == "auto":
    #             _type_content_output = "Điểm danh tự động"
    #         else:
    #             _type_content_output = "Điểm danh qua phản hồi"
    #
    #         not_success = " không thành công:"
    #         success = " thành công"
    #
    #         if _type_emp == "official":
    #             # queryset = EmpCheckin.objects.all() cau query lay full data
    #             queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
    #             serializer = EmpCheckinSerializer(queryset, many=True)
    #             data_query = serializer.data
    #
    #             if len(data_query) > 0:
    #                 data_checkin = data_query[0]
    #                 # print(data_checkin)
    #
    #                 id_checkin = data_checkin['id']
    #                 emp_id = data_checkin['accountNameMBN']
    #                 res_time = time__
    #                 ca = data_checkin['sheetTime']
    #                 coordinate_office = data_checkin['coordinateOffice']
    #                 block_name = data_checkin['blockName']
    #                 block_distance = data_checkin['blockDistance']
    #                 coordinate_block = data_checkin['coordinateBlock']
    #                 count_auto = data_checkin['countAuto']
    #                 count_response = data_checkin['countResponse']
    #                 team_name = data_checkin['teamName']
    #                 checkin_success = data_checkin['checkinSuccess']
    #
    #                 if ca != "O":
    #                     if checkin_success != "OK":
    #
    #                         if type_checkin == "auto":
    #                             count_auto = count_auto + 1
    #                         else:
    #                             count_response = count_response + 1
    #
    #                         reason_failed = ""
    #                         # add_checkin = ""
    #
    #                         # xu ly vi tri
    #
    #                         dict_position = calculcate_distance_for_official_emp(emp_coordinate=coordinate,block_center=coordinate_block,block_distance=block_distance,office_center=coordinate_office,block_name=block_name)
    #                         status_position = dict_position["checkin"]
    #                         add_checkin = dict_position['location']
    #
    #
    #                         if not status_position:
    #                             # reason_failed = "VỊ TRÍ ĐIỂM DANH KHÔNG PHÙ HỢP"
    #                             # check_in = "NOT OK"
    #                             # status = 0
    #                             return response_data(data={}, message="Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc", status=STATUS_CODE_INVALID_INPUT)
    #                         else:
    #                             dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now, ca, add_checkin)
    #                             status = dict_data_workday['status']
    #                             check_in = dict_data_workday['check_in']
    #
    #
    #
    #                             workday_convert = status
    #                             if status < 0.7:
    #                                 workday_convert = 0
    #
    #
    #                             EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
    #                                 checkin_success=check_in,
    #                                 workday_factor=status,
    #                                 workday_convert=workday_convert,
    #                                 checkin_time=res_time,
    #                                 location=add_checkin,
    #                                 count_auto=count_auto,
    #                                 count_response=count_response)
    #
    #                             # _type_content_output = _type_content_output + success
    #                             # status_checkin = 1
    #                             # status_api = 1
    #                             # content_output = _type_content_output + success
    #
    #                             date_now = get_current_date()
    #                             str_time_now_new = date_now.strftime('%d/%m/%Y')
    #                             params = {
    #                                     "email": user_email,
    #                                     "title": "Điểm danh thành công",
    #                                     "body": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(res_time, str_time_now_new),
    #                                     "notificationLayout": ""
    #                             }
    #                             msg = call_api_noti_success_checkin(params)
    #                             print("-----------------------BAN NOT -------------------------")
    #                             print(msg)
    #                             return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
    #
    #
    #                     else:
    #                         content_output = "Bạn đã điểm danh"
    #                         return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #                 else:
    #                     content_output = "Hệ thống sẽ không ghi nhận điểm danh khi nhân viên không có lịch trực trong ngày. Mọi thắc mắc xin vui lòng liên hệ Admin chi nhánh"
    #                     return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #
    #             else:
    #                 content_output = "Hệ thống sẽ không ghi nhận điểm danh khi nhân viên không có lịch trực trong ngày. Mọi thắc mắc xin vui lòng liên hệ Admin chi nhánh"
    #                 return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #
    #         else:
    #
    #             ca = "S"
    #             full_date = __day.split("-")
    #             _year = full_date[0]
    #             _month = full_date[1]
    #             _day = full_date[2]
    #             emp_checkin_class = EmpCheckin()
    #             # queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
    #             queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day)
    #             serializer = EmpCheckinSerializer(queryset, many=True)
    #             data_query = serializer.data
    #
    #             note = ""
    #
    #             ok_continue = True
    #
    #             if len(data_query) == 0:
    #                 emp_checkin_class.emp_code = emp_code
    #                 # emp_checkin_class.MBN_account_name = emp_id
    #                 emp_checkin_class.checkin_date = __day
    #                 emp_checkin_class.checkin_day = _day
    #                 emp_checkin_class.checkin_month = _month
    #                 emp_checkin_class.checkin_year = _year
    #                 emp_checkin_class.sheet_time = ca
    #                 emp_checkin_save = emp_checkin_class.save(force_update=False)
    #
    #                 count_auto = 0
    #                 count_response = 0
    #
    #                 if type_checkin == "auto":
    #                     count_auto = count_auto + 1
    #                 else:
    #                     count_response = count_response + 1
    #             else:
    #                 note = data_query[0]['note']
    #                 count_auto = data_query[0]['countAuto']
    #                 count_response = data_query[0]['countResponse']
    #                 checkin_success = data_query[0]['checkinSuccess']
    #                 if checkin_success == "OK":
    #                     ok_continue = False
    #                 if type_checkin == "auto":
    #                     count_auto = count_auto + 1
    #                 else:
    #                     count_response = count_response + 1
    #
    #             # print(emp_code)
    #             # kiem tra da diem danh hay chua
    #             if ok_continue:
    #                 queryset_info_checkin_condition = AccountManagement.objects.filter(emp_code=emp_code)
    #                 serializer_checkin_condition = AccountManagemenSerializer(queryset_info_checkin_condition,
    #                                                                           many=True)
    #                 data_query_checkin_condition = serializer_checkin_condition.data
    #
    #                 if len(data_query_checkin_condition) != 0:
    #                     info_checkin = data_query_checkin_condition[0]
    #                     toa_do_van_phong = info_checkin['coordinateOffice']
    #                     toa_do_kho = info_checkin['coordinateWarehouse']
    #                     toa_do_lam_viec = info_checkin['coordinateWorking']
    #                     ban_kinh_lam_viec = info_checkin['workingRadius']
    #                     emp_id = info_checkin['accountNameMBN']
    #                     team_name = get_branch_fr_account_mobinet(emp_id)
    #
    #                     # data_position = calculate_distance_for_new_emp(coordinate, toa_do_van_phong, toa_do_kho,
    #                     #                                                toa_do_lam_viec, ban_kinh_lam_viec)
    #
    #                     data_position = calculate_distance_for_new_emp(coor_emp=coordinate,toa_do_van_phong=toa_do_van_phong,
    #                                                                    toa_do_kho=toa_do_kho, toa_do_lam_viec=toa_do_lam_viec,str_ban_kinh_lam_viec=ban_kinh_lam_viec)
    #
    #                     data_status_checkin = data_position.get("checkin", "NOT OK")
    #
    #                     location = data_position.get("location", "")
    #                     if location == "BLOCK":
    #                         block_name = "BLOCK"
    #                     else:
    #                         block_name = ""
    #                     # if emp_id != "":
    #                     #     team_name = str(emp_id).split(".")[0]
    #                     if data_status_checkin == "OK":
    #
    #                         data_workday = calculate_workday_factor(branch, str_time_now, ca, coordinate)
    #                         workday_factor = data_workday.get('workday', 0)
    #                         # too_late = data_workday.get('too_late')
    #
    #                         EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
    #                             MBN_account_name=emp_id, team_name=team_name,
    #                             block_name=block_name,
    #                             checkin_success=data_status_checkin,
    #                             workday_factor=workday_factor,
    #                             workday_convert=workday_factor,
    #                             checkin_time=time__,
    #                             location=location,
    #                             count_auto=count_auto,
    #                             count_response=count_response)
    #
    #
    #                         content_output = _type_content_output + success
    #
    #
    #                         date_now = get_current_date()
    #                         str_time_now_new = date_now.strftime('%d/%m/%Y')
    #                         params = {
    #                             "topic": "checkin_ok",
    #                             "time": time__,
    #                             "date": str_time_now_new
    #                         }
    #                         msg = call_api_noti_success_checkin(headerAuthToken, params)
    #                         date_now = get_current_date()
    #                         str_time_now_new = date_now.strftime('%d/%m/%Y')
    #                         params = {
    #                             "topic": "checkin_ok",
    #                             "time": time__,
    #                             "date": str_time_now_new
    #                         }
    #                         msg = call_api_noti_success_checkin(headerAuthToken, params)
    #                         print("-----------------------BAN NOT -------------------------")
    #                         print(msg)
    #                         return response_data(data={}, message=content_output, status=STATUS_CODE_SUCCESS)
    #
    #                     else:
    #                         content_output = "Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc"
    #                         return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #
    #
    #                 else:
    #                     content_output = "Không tìm thấy thông tin về địa điểm điểm danh của bạn"
    #                     return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #             else:
    #                 content_output = "Bạn đã điểm danh"
    #                 return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
    #
    #
    #
    #
    #         # insert_log_get_coordinate(str_time_now, type_checkin, coordinate, status_checkin, __day, emp_code) # luu log lich su
    #
    #     except Exception as e:
    #         print("---------------get_coordinate----------------------")
    #         print(e)
    #         return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)
    #
    #
    #     # lay data
    #     # k = serializer.data
    #     # print(k[0]['id'])
    #
    #     # data = {
    #     #     "contentNoti": content_output,
    #     # }



