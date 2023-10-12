from rest_framework.viewsets import ViewSet
from ...core.helpers.response import *
from ...cron import *
import requests
from ..models.emp_checkin import *
from ..models.account_management_tb import *
from ..serializers.emp_checkin_serializer import *
from ..serializers.account_management_serializer import *
from ...core.helpers.utils import *
from ...core.helpers.utils_sql import *
from ...core.helpers.call_api import *
from ...core.helpers.schedule import mypt_schedule
import json


class CronView(ViewSet):
    def cron_old(self, request):
        try:
            str_date_now_db = get_str_date_now_import_db()
            time_now = get_current_datetime()
            int_time_hour = date_time_to_hour(time_now)
            if int_time_hour >=5 and int_time_hour <=17:
                str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
                time__ = str_time_now.split(" ")[1]
                res_time = time__
                queryset = EmpCheckin.objects.filter(checkin_date=str_date_now_db).exclude(checkin_success="OK")
                serializer = EmpCheckinSerializer(queryset, many=True)
                data = serializer.data
                # print(data)
                list_mbn = []
                # list_emp_code = []
                # print(str_time_now)
                # print("-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
                if len(data) > 0:


                    for item in data:
                        list_mbn.append(item['accountNameMBN'])
                        # list_emp_code.append(item['code'])
                    queryset_account = AccountManagement.objects.filter(MBN_account_name__in=tuple(list_mbn))
                    serializer_account = AccountManagemenSerializer(queryset_account, many=True)
                    list_data_acc = serializer_account.data
                    # dict_data_token = {}
                    dict_data_device_name = {}
                    # print(list_emp_code)

                    if len(list_data_acc) > 0:
                        for i_acc in list_data_acc:
                            emp_code_token = i_acc['code']
                            device_token = i_acc['deviceToken']
                            device_name = i_acc['deviceName']
                            # dict_data_token.update({
                            #     emp_code_token: device_token
                            # })
                            dict_data_device_name.update({
                                emp_code_token: device_name
                            })


                    response = call_api(
                        host = "https://trackingapi.fpt.vn/",
                        func = "api/getLocationUsers",
                        method = "POST",
                        data = {"EmpID":list_mbn}
                    )
                    dataApi = json.loads(response)
                    print("=====================================BAN API THANH CONG==============================")
                    # print(dataApi)
                    # print(list_mbn)
                    # dataApi = {
                    #        "ErrorCode":0,
                    #        "message":"Thành công!",
                    #        "result":[
                    #           {
                    #              "mobiAccount":"PNC11.TUANHT",
                    #              "location":"10.782159745279957, 106.6616478625851",
                    #              "time":"2022-08-05T08:02:18+07:00"
                    #           }
                    #        ]
                    # }

                    result_data = dataApi.get("result", [])
                    error_code_api = dataApi.get("ErrorCode", 1)
                    list_noti = []
                    if error_code_api == 0:
                        # print("-----gggggggggggggggggggggggggggggggggggg--------------------------")
                        if result_data is not None:
                            # print("-----tttttttttttttttttttttttt--------------------------")
                            if len(result_data)>0:
                                # print("-----tttttttttttttttttttttttt44444444444444444444444444444--------------------------")
                                for i_data in result_data:
                                    acc_mobinet = i_data.get('mobiAccount')
                                    if not is_null_or_empty(acc_mobinet):
                                        emp_coordinate = i_data.get('location')
                                        if not check_input_toa_do(emp_coordinate):
                                            continue
                                        index_list = list_mbn.index(acc_mobinet)
                                        dict_data_emp = data[index_list]
                                        block_center = dict_data_emp['coordinateBlock']
                                        office_center = dict_data_emp['coordinateOffice']
                                        block_distance = dict_data_emp['blockDistance']
                                        block_name = dict_data_emp['blockName']
                                        ca = dict_data_emp['sheetTime']
                                        checkin_success = dict_data_emp['checkinSuccess']
                                        team_name = dict_data_emp['teamName']
                                        emp_code = dict_data_emp['code']
                                        history_coordiante = dict_data_emp['historyCoordinate']
                                        if ca != "O":
                                            if checkin_success != "OK":



                                                reason_failed = ""
                                                # add_checkin = ""

                                                # xu ly vi tri

                                                dict_position = calculcate_distance_for_official_emp(emp_coordinate=emp_coordinate,block_center=block_center,
                                                                                                     block_distance=block_distance,office_center=office_center,block_name=block_name)
                                                status_position = dict_position["checkin"]
                                                add_checkin = dict_position['location']

                                                if status_position == "NOTOK":
                                                    pass
                                                    # reason_failed = "VỊ TRÍ ĐIỂM DANH KHÔNG PHÙ HỢP"
                                                    # check_in = "NOT OK"
                                                    # status = 0
                                                    # return response_data(data={"detail":"Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc"}, message= MESSAGE_API_FAILED_CHECKIN, status=STATUS_CODE_INVALID_INPUT)
                                                else:
                                                    dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now, ca, add_checkin)
                                                    status = dict_data_workday['status']
                                                    check_in = dict_data_workday['check_in']
                                                    # print(134)



                                                    workday_convert = status
                                                    # if status < 0.7:
                                                    #     workday_convert = 0


                                                    EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=str_date_now_db).update(
                                                        checkin_success=check_in,
                                                        workday_factor=status,
                                                        workday_convert=workday_convert,
                                                        checkin_time=res_time,
                                                        location=add_checkin, count_response=99)

                                                    # _type_content_output = _type_content_output + success
                                                    # status_checkin = 1
                                                    # status_api = 1
                                                    # content_output = _type_content_output + success

                                                    date_now = get_current_date()
                                                    str_time_now_new = date_now.strftime('%d/%m/%Y')

                                                    # device_token_emp = dict_data_token.get(emp_code)
                                                    # print("=====================device token")
                                                    # print(device_token_emp)
                                                    # print(dict_data_token)
                                                    # print(161)
                                                    # if not is_null_or_empty(device_token_emp):
                                                    params = {
                                                            # "deviceToken": device_token_emp,
                                                            "emp_code": emp_code,
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
                                                    # print(params)
                                                    # msg = call_api_noti_success_checkin(params)
                                                    print("-----------------------BAN NOT -------------------------")
                                                    # print(msg)
                                                    list_noti.append(params)
                                                    # return response_data(data={"detail": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(res_time, str_time_now_new)}, message=MESSAGE_API_SUCCESS_CHECKIN, status=STATUS_CODE_SUCCESS)


                                            else:
                                                content_output = "Bạn đã điểm danh"
                                                # return response_data(data={}, status=STATUS_CODE_INVALID_INPUT, message=content_output)
                                        else:
                                            device_name_acc = dict_data_device_name.get(emp_code)
                                            save_db_shift_off_new(history_coordiante, res_time, emp_coordinate, emp_code,
                                                                  str_date_now_db, block_distance, block_center, office_center,
                                                                  block_name, team_name, str_time_now, ca, device_name_acc)
                                            # save_db_shift_off_new(history_coordiante,res_time, emp_coordinate, emp_code,
                                            #                       str_date_now_db, block_distance, block_center, office_center,
                                            #                       block_name, team_name, str_time_now, ca, device_name_acc)


                            # for item in serializer.data:
                                # dict_position = calculcate_distance_for_official_emp(emp_coordinate=dataApi.pop(),block_center=item["coordinateWorking"],block_distance=item["workingRadius"],office_center=item["coordinateWorking"],block_name=item["blockName"])

                            if len(list_noti) > 0:
                                params = {
                                    "data": list_noti
                                }
                                msg = call_api_change_shift(params=params)
                                # print("------------------BAN NOTI------------------------")
                                # print(msg)
                            return response_data("serializer.data")
                        else:
                            return response_data("Không lấy được data")
                    else:
                        return response_data(data='loi khi ban api tracking', message="", status=0)
                else:
                    return response_data(data='khong co thong tin', message="", status=0)
            else:
                return response_data(data="chua den gio", message="chua den gio", status=0)
        except Exception as ex:
            print("==========================================LOI")
            print(ex)
            return response_data(data=str(ex), message="", status=0)

    def cron(self, request):
        try:
            # diem danh theo TIN hoac PNC
            str_date_now_db = get_str_date_now_import_db()
            time_now = get_current_datetime()
            str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
            time__ = str_time_now.split(" ")[1]
            res_time = time__

            # xu ly danh cho PNC
            queryset = EmpCheckin.objects.filter(checkin_date=str_date_now_db).exclude(
                team_name__in=tuple(LIST_BLOCK)).exclude(checkin_success="OK")
            serializer = EmpCheckinSerializer(queryset, many=True)

            data = serializer.data
            print("====================PNC=======================")
            # print(data)
            list_mbn = []
            # list_emp_code = []
            list_PNC = []
            status_PNC = 0
            # print(str_time_now)
            # print("-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
            if len(data) > 0:

                cron_update_coordinate(data, str_date_now_db, str_time_now, res_time, "PNC")
            else:
                print("khong co thong tin cho diem danh tu dong PNC")
                # return response_data(data='khong co thong tin', message="", status=0)

            # xu ly danh cho TIN
            queryset = EmpCheckin.objects.filter(checkin_date=str_date_now_db, team_name__in=tuple(LIST_BLOCK)).exclude(
                checkin_success="OK")

            serializer = EmpCheckinSerializer(queryset, many=True)
            data = serializer.data
            print("====================TIN=======================")
            # print(data)
            list_mbn = []
            # list_emp_code = []
            list_TIN = []
            status_TIN = 0
            # print(str_time_now)
            # print("-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
            if len(data) > 0:

                cron_update_coordinate(data, str_date_now_db, str_time_now, res_time, "TIN")
            else:
                print("khong co thong tin cho diem danh tu dong TIN")
                # return response_data(data='khong co thong tin', message="", status=0)

            return response_data(data="", message="THANH CONG", status=1)





        except Exception as ex:
            print("==========================================LOI")
            print(ex)
            return response_data(data=str(ex), message="", status=0)
    
    def test1(self):
        response = self.call_api()
        print (response)
        
    def call_api(self):
        print("================start cron================")
        print(get_current_datetime())
        if APP_ENV == "production":
            url = "http://myptpdx-api.fpt.net/mypt-checkin-api/v1/cron"
        else:
            url = "http://myptpdx-api-stag.fpt.net/mypt-checkin-api/v1/cron"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload, verify = False)
        return response.text
    
    tasks = MYPTCron()
    def cron_start(self, request):
        # return response_data(calculcate_distance_for_official_emp())
        # self.tasks.stop()
        # self.tasks.add_job(self.test1, '* * * * * *')
        # self.tasks.start()
        # str_date_now_db = get_str_date_now_import_db()
        # time_now = get_current_datetime()
        # str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
        # time__ = str_time_now.split(" ")[1]
        print("DA START CRONE")
        schedule_time = {
            "time_frame": True,
            "run_type": "every_minute",
            "interval": 1,
            "at": ":00",
            "start_at": "05:00:00",
            "until": "18:00:00"
        }
        mypt_schedule.add_task(self.test1, schedule_time)
        
        return response_data()