from app.http.serializers.emp_checkin_history_serializer import *
from app.http.serializers.emp_checkin_serializer import *
from app.http.serializers.account_management_serializer import *
from app.http.serializers.emp_response_serializer import *
from app.core.helpers.utils import *
from app.core.helpers.call_api import *
from core.helpers.response import *

def insert_log_get_coordinate(str_time_now, type_checkin, coordinate, status_checkin, __day, emp_code):
    ok = False
    history_checkin = empCheckinHistory()
    history_checkin.update_time = str_time_now
    history_checkin.type_checkin = type_checkin
    history_checkin.coordinate = coordinate
    history_checkin.status = status_checkin
    history_checkin.checkin_date = __day
    history_checkin.emp_code = emp_code
    history_checkin.save()
    ok = True
    return ok


def info_history_checkin_on_month_now(list_data, emp_code,  fname):
    # queryset_device = AccountManagement.objects.filter(emp_code=emp_code)
    # serializer_device = AccountManagemenSerializer(queryset_device, many=True)
    # list_data_device = serializer_device.data
    # device_name = ""
    # if len(list_data_device) > 0:
    #     device_name = list_data_device[0]['deviceName']

    list_info_checkin = []

    count_ontime = 0
    count_late = 0
    count_off = 0
    count_workday = 0
    count_notcheckin = 0
    percent_abide = 0
    percent_not_abide = 0

    str_date_now = get_str_date_now_import_db()
    for i in list_data:
        checkin_date = i['checkinDate']
        workday_convert = i['workdayConvert']
        ca = i['sheetTime']
        block_name = i['blockName']
        checkin_time = i['checkinTime']
        device_name = i['deviceName']

        if ca != "O":

            if workday_convert is not None:
                if workday_convert == 1:
                    status_checkin = "ontime"
                    count_ontime = count_ontime + 1
                else:
                    status_checkin = "late"
                    count_late = count_late + 1
            else:
                status_checkin = "notcheckin"
                count_notcheckin = count_notcheckin + 1
        else:
            status_checkin = "off"
            count_off = count_off + 1
        if not is_null_or_empty(workday_convert):
            count_workday = count_workday + workday_convert


        thu = get_type_date_fr_str_date(checkin_date, fname)
        if not is_null_or_empty(thu):
            thu = thu.title()
        str_date = thu + ", Ngày " + checkin_date

        _date_checkin_date = datetime.strptime(checkin_date, "%d/%m/%Y").strftime('%Y-%m-%d')

        if str_date_now == _date_checkin_date:
            checkin_success = i['checkinSuccess']
            if checkin_success == "NOT OK" and ca != "O":
                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": checkin_date,
                    "status": "notcheckin",
                    "deviceName": "",
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0.0
                })
            else:
                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": checkin_date,
                    "status": status_checkin,
                    "deviceName": device_name,
                    "location": block_name,
                    "timeCheckin": checkin_time,
                    "numWorkday": workday_convert
                })

        else:
            list_info_checkin.append({
                "dateDetail": str_date,
                "date": checkin_date,
                "status": status_checkin,
                "deviceName": device_name,
                "location": block_name,
                "timeCheckin": checkin_time,
                "numWorkday": workday_convert
            })

    percent_abide = round(count_ontime / (count_late + count_ontime + count_notcheckin) * 100)
    percent_not_abide = 100 - percent_abide

    # list_info_checkin = preprocess_list_data_history_checkin_on_month_now(list_info_checkin, device_name)

    dict_info_output = {
        "countLate": count_late,
        "countOnTime": count_ontime,
        "countOff": count_off,
        "countWorkday": round(count_workday, 2),
        "percentAbide": percent_abide,
        "percentNotAbide": percent_not_abide,
        "listEvent": list_info_checkin

    }
    return dict_info_output


def info_history_checkin_on_month(list_data, emp_code, fname):


    list_info_checkin = []

    count_ontime = 0
    count_late = 0
    count_off = 0
    count_workday = 0
    count_notcheckin = 0
    percent_abide = 0
    percent_not_abide = 0
    for i in list_data:
        checkin_date = i['checkinDate']
        workday_convert = i['workdayConvert']
        ca = i['sheetTime']
        block_name = i['blockName']
        checkin_time = i['checkinTime']
        device_name = i['deviceName']
        if ca != "O":
            if workday_convert is not None:
                if workday_convert == 1:
                    status_checkin = "ontime"
                    count_ontime = count_ontime + 1
                else:
                    status_checkin = "late"
                    count_late = count_late + 1
            else:
                status_checkin = "notcheckin"
                count_notcheckin = count_notcheckin + 1

        else:
            status_checkin = "off"
            count_off = count_off + 1

        thu = get_type_date_fr_str_date(checkin_date, fname)
        if not is_null_or_empty(thu):
            thu = thu.title()
        str_date = thu + ", Ngày " + checkin_date

        # _date_checkin_date = datetime.strptime(checkin_date, "%d/%m/%Y").strftime('%Y-%M-%d')
        list_info_checkin.append({
            "dateDetail": str_date,
            "date": checkin_date,
            "status": status_checkin,
            "deviceName": device_name,
            "location": block_name,
            "timeCheckin": checkin_time,
            "numWorkday": workday_convert
        })

        # count_workday = count_workday + workday_convert
        if not is_null_or_empty(workday_convert):
            count_workday = count_workday + workday_convert
    percent_abide = round(count_ontime / (count_late + count_ontime + count_notcheckin) * 100)

    percent_not_abide = 100 - percent_abide

    # list_info_checkin = preprocess_list_data_history_checkin_on_month(list_info_checkin, device_name )

    dict_info_output = {
        "countLate": count_late,
        "countOnTime": count_ontime,
        "countOff": count_off,
        "countWorkday": round(count_workday,2),
        'percentAbide': percent_abide,
        'percentNotAbide': percent_not_abide,
        "listEvent": list_info_checkin

    }

    return dict_info_output

def save_db_shif_off(history_coordiante, res_time, coordinate, emp_code, __day):
    if not is_null_or_empty(history_coordiante):
        list_history = eval(history_coordiante)
        list_history.append({
            'res_time': res_time,
            'coordinate': coordinate
        })
    else:
        list_history = [{
            'res_time': res_time,
            'coordinate': coordinate
        }]
    EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(history_coordinate=list_history)


def save_db_shift_off_new(history_coordiante, res_time, coordinate, emp_code,
                          __day, block_distance, coordinate_block, coordinate_office,
                          block_name, team_name, str_time_now, ca, device_name):
    if is_null_or_empty(coordinate_office) or is_null_or_empty(coordinate_block) or is_null_or_empty(block_distance):
        print("====================== rong")
        return "Thông tin không phù hơp"

    if not check_input_toa_do(coordinate_office) or not check_input_toa_do(coordinate_block):
        print("----------sai")
        return "Tọa độ không phù hơp"

    dict_position = calculcate_distance_for_official_emp(emp_coordinate=coordinate, block_center=coordinate_block,
                                                         block_distance=block_distance, office_center=coordinate_office,
                                                         block_name=block_name)
    status_position = dict_position["checkin"]
    add_checkin = dict_position['location']

    list_history = []

    # time_now = get_current_datetime()
    # str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
    # time__ = str_time_now.split(" ")[1]

    if status_position == "NOTOK":
        # reason_failed = "VỊ TRÍ ĐIỂM DANH KHÔNG PHÙ HỢP"
        # check_in = "NOT OK"
        # status = 0
        return response_data(
            data={"detail": "Vị trí điểm danh chưa phù hợp. Vui lòng di chuyển gần hơn vào khu vực bạn làm việc"},
            message=MESSAGE_API_FAILED_CHECKIN, status=STATUS_CODE_INVALID_INPUT)
    else:
        dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now, ca, add_checkin)
        status = dict_data_workday['status']
        check_in = dict_data_workday['check_in']
        print(check_in)

        workday_convert = status

        if check_in == "OK":
            list_history.append({
                'workday_convert': status,
                'workday_factor': workday_convert,
                "res_time": res_time,
                "ca": "C"
            })

        dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now, "S", add_checkin)
        status = dict_data_workday['status']
        check_in = dict_data_workday['check_in']
        print(check_in)

        workday_convert = status
        if check_in == "OK":
            list_history.append({
                'workday_convert': status,
                'workday_factor': workday_convert,
                "res_time": res_time,
                "ca": "S"
            })




        # if status < 0.7:
        #     workday_convert = 0

    # if not is_null_or_empty(history_coordiante):
    #     list_history = eval(history_coordiante)
    #     info_his = list_history[0]
    #     if check_in == "OK":
    #
    #
    # else:
    #     list_history = [{
    #         'res_time': res_time,
    #         'coordinate': coordinate
    #     }]

    # neu diem danh thanh cong thi luu vao db
    if check_in == "OK":
        if is_null_or_empty(history_coordiante):
            # list_history = [{
            #         'workday_convert': status,
            #         'workday_factor': workday_convert
            #     }]
            # print(list_history)

            EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(history_coordinate=list_history, device_name=device_name)
            if len(list_history) > 0:
                EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(checkin_success="OK")
    else:
        EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=__day).update(
                                                                                device_name=device_name)


def preprocess_list_data_history_checkin_on_month_old(list_info_checkin, device_name):
    str_start_date = list_info_checkin[0]['date']
    str_end_date = list_info_checkin[-1]['date']
    month_input = str_start_date.split("/")[1]
    year_input = str_start_date.split("/")[2]
    if str_start_date != "01/{}/{}".format(month_input, year_input):
        str_start_date = "01/{}/{}".format(month_input, year_input)
    start_date = convert_str_to_date(str_start_date)
    end_date = convert_str_to_date(str_end_date)

    # date_now = get_current_date()
    str_date_now = get_str_date_now_export()
    month_now = str_date_now.split("/")[1]
    year_now = str_date_now.split("/")[2]




    date_generated = [start_date + timedelta(days=x) for x in
                      range(0, (end_date - start_date).days)]
    list_str_date_generate = []
    for k in date_generated:
        str_k = convert_date_export(k)
        list_str_date_generate.append(str_k)

    # str_date_now = get_str_date_now_export()
    date_now = get_current_date()
    if year_now == year_input and month_now == month_input:
        if str_date_now not in list_str_date_generate:
            list_str_date_generate.append(str_date_now)


    list_info_checkin_output = list_info_checkin.copy()

    list_date = []
    for i in list_info_checkin:
        date_ = i['date']
        list_date.append(date_)

    for i_date in list_str_date_generate:
        print(i_date not in list_date)
        if i_date not in list_date:
            thu = get_type_date_fr_str_date(i_date, '')
            if not is_null_or_empty(thu):
                thu = thu.title()
            str_date = thu + ", Ngày " + i_date
            date_init = convert_str_to_date(i_date)
            if date_init < date_now:
                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": i_date,
                    "status": "off",
                    "deviceName": device_name,
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0
                })
            else:

                list_info_checkin.append({
                        "dateDetail": str_date,
                        "date": i_date,
                        "status": "notcheckin",
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })



        # for i_date in list_str_date_generate:
        #     if i_date != date_:
        #
        #         thu = get_type_date_fr_str_date(i_date, '')
        #         if not is_null_or_empty(thu):
        #             thu = thu.title()
        #         str_date = thu + ", Ngày " + i_date
        #         list_info_checkin_output.append({
        #             "dateDetail": str_date,
        #             "date": i_date,
        #             "status": "off",
        #             "deviceName": device_name,
        #             "location": "",
        #             "timeCheckin": "",
        #             "numWorkday": 0
        #         })

    list_info_checkin = sorted(list_info_checkin, key=lambda k: convert_str_to_date(k['date']))


    return list_info_checkin


def preprocess_list_data_history_checkin_on_month(list_info_checkin, device_name):


    # xu ly nhung ngay ko co trong data diem danh
    list_info_checkin = sorted(list_info_checkin, key=lambda k: convert_str_to_date(k['date']))
    str_start_date = list_info_checkin[0]['date']
    str_end_date = list_info_checkin[-1]['date']
    # print(list_info_checkin)
    # print(str_end_date)
    month_input = str_start_date.split("/")[1]
    year_input = str_start_date.split("/")[2]
    if str_start_date != "01/{}/{}".format(month_input, year_input):
        str_start_date = "01/{}/{}".format(month_input, year_input)
    start_date = convert_str_to_date(str_start_date)
    end_date = convert_str_to_date(str_end_date)

    # date_now = get_current_date()
    str_date_now = get_str_date_now_export()
    month_now = str_date_now.split("/")[1]
    year_now = str_date_now.split("/")[2]

    date_generated = [start_date + timedelta(days=x) for x in
                      range(0, (end_date - start_date).days + 1)]
    list_str_date_generate = []
    for k in date_generated:
        str_k = convert_date_export(k)
        list_str_date_generate.append(str_k)

    # str_date_now = get_str_date_now_export()
    date_now = get_current_date()
    if year_now == year_input and month_now == month_input:
        if str_date_now not in list_str_date_generate:
            list_str_date_generate.append(str_date_now)



    list_date = []
    for i in list_info_checkin:
        date_ = i['date']
        list_date.append(date_)
    print(list_date)
    print(list_str_date_generate)

    cnt_off = 0
    for i_date in list_str_date_generate:
        # print(i_date not in list_date)
        if i_date not in list_date:
            thu = get_type_date_fr_str_date(i_date, '')
            if not is_null_or_empty(thu):
                thu = thu.title()
            str_date = thu + ", Ngày " + i_date
            date_init = convert_str_to_date(i_date)
            if date_init < date_now:
                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": i_date,
                    "status": "off",
                    "deviceName": '',
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0
                })
                cnt_off = cnt_off + 1
            else:

                list_info_checkin.append({
                        "dateDetail": str_date,
                        "date": i_date,
                        "status": "notcheckin",
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })



        # for i_date in list_str_date_generate:
        #     if i_date != date_:
        #
        #         thu = get_type_date_fr_str_date(i_date, '')
        #         if not is_null_or_empty(thu):
        #             thu = thu.title()
        #         str_date = thu + ", Ngày " + i_date
        #         list_info_checkin_output.append({
        #             "dateDetail": str_date,
        #             "date": i_date,
        #             "status": "off",
        #             "deviceName": device_name,
        #             "location": "",
        #             "timeCheckin": "",
        #             "numWorkday": 0
        #         })

    list_info_checkin = sorted(list_info_checkin, key=lambda k: convert_str_to_date(k['date']))


    return list_info_checkin, cnt_off

def history_checkin_on_month_past(year_input, month_input, emp_code, device_name, str_start_contract, checkin_date_first, checkin_date_first_date, fname):
    _date_input = str(year_input) + "-" + month_input
    queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__startswith=_date_input).order_by(
        'checkin_date')

    serializer = EmpCheckinSerializer(queryset, many=True)
    list_data = serializer.data
    if len(list_data) > 0:
        dict_info_output = info_history_checkin_on_month(list_data, emp_code, device_name,
                                                         fname)
        dict_info_output.update({
            'firstWorkdate': str_start_contract
        })

        month_start_checkin = checkin_date_first.split("/")[1]
        year_start_checkin = checkin_date_first.split("/")[2]

        # print(int(month_start_checkin) < int(month_input))
        # print(month_start_checkin)
        # print(month_input)

        if month_start_checkin == month_input:
            # ngay ky hop dong ma ko di lam
            str_start_contract = "01/{}/{}".format(month_start_checkin, year_start_checkin)
            start_contract = convert_str_to_date(str_start_contract)
            date_generated = [start_contract + timedelta(days=x) for x in
                              range(0, (checkin_date_first_date - start_contract).days)]
            list_event = dict_info_output.get('listEvent', [])
            # print("===================++++")
            # print(list_event)
            cnt_off = 0
            if len(date_generated) > 0:

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
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })
                    cnt_off = cnt_off + 1
                # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            # list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(
            #     list_event, device_name)
            # dict_info_output['listEvent'] = list_event
            # # dict_info_output['listEvent'] = list_event
            # dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
            list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
            # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            dict_info_output['listEvent'] = list_event
            dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
            tuan_thu = dict_info_output['countOff'] + dict_info_output['countOnTime']
            percent_tuan_thu = tuan_thu / len(list_event)
            print( len(list_event))
            print(dict_info_output['countOff'] + dict_info_output['countOnTime'])
            dict_info_output['percentAbide'] = round(percent_tuan_thu, 2)
            dict_info_output['percentNotAbide'] = 100 - round(percent_tuan_thu, 2)
            return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                 status=STATUS_CODE_SUCCESS)

        elif int(month_start_checkin) < int(month_input):


            # ngay ky hop dong ma ko di lam
            # start_contract = convert_str_to_date(str_start_contract)
            # % d / % m / % Y

            str_start_contract = "01/{}/{}".format(month_input, year_start_checkin)

            start_contract = convert_str_to_date(str_start_contract)
            date_generated = [start_contract + timedelta(days=x) for x in
                              range(0, (checkin_date_first_date - start_contract).days)]

            list_event = dict_info_output.get('listEvent', [])

            cnt_off = 0
            if len(date_generated) > 0:

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
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })
                    cnt_off = cnt_off + 1
                # list_event = preprocess_list_data_history_checkin_on_month(list_event, device_name)
                # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            dict_info_output['listEvent'] = list_event

            # list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
            list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
            # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            dict_info_output['listEvent'] = list_event
            dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
            tuan_thu = dict_info_output['countOff'] + dict_info_output['countOnTime']
            percent_tuan_thu = tuan_thu / len(list_event)
            dict_info_output['percentAbide'] = round(percent_tuan_thu, 2)
            dict_info_output['percentNotAbide'] = 100 - round(percent_tuan_thu, 2)
            return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                 status=STATUS_CODE_SUCCESS)

            # =========================================

            # dict_info_output = info_history_checkin_on_month(list_data, emp_code, device_name, fname)
            # dict_info_output.update({
            #     'firstWorkdate': checkin_date_first
            # })

        else:
            return response_data(data={'firstWorkdate': str_start_contract},
                                 message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)


    else:
        dict_output = info_history_month_not_start_checkin(str_start_contract, year_input, month_input, device_name)
        dict_output.update({
            'firstWorkdate': str_start_contract
        })

        return response_data(data=dict_output, message=MESSAGE_API_NO_DATA,
                             status=STATUS_CODE_NO_DATA)


def history_checkin_on_month_now(year_input, month_input, emp_code, device_name, str_start_contract, checkin_date_first, checkin_date_first_date, fname):
    from_date = str(year_input) + "-" + month_input + "-" + "01"
    to_date = get_str_date_now_import_db()
    queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__range=[from_date, to_date]).order_by(
        'checkin_date')
    # print(queryset.query)

    serializer = EmpCheckinSerializer(queryset, many=True)
    list_data = serializer.data
    if len(list_data) > 0:
        # lay thong tin thiet bi thiet bi
        dict_info_output = info_history_checkin_on_month_now(list_data, emp_code, device_name, fname)
        dict_info_output.update({
            'firstWorkdate': str_start_contract
        })

        # xu ly truong hop ngay dau tien di lam ma ko diem danh
        month_start_checkin = checkin_date_first.split("/")[1]
        year_start_checkin = checkin_date_first.split("/")[2]

        if month_start_checkin == month_input:
            # ngay ky hop dong ma ko di lam
            # start_contract = convert_str_to_date(str_start_contract)
            # % d / % m / % Y
            str_start_contract = "01/{}/{}".format(month_start_checkin, year_start_checkin)
            start_contract = convert_str_to_date(str_start_contract)
            date_generated = [start_contract + timedelta(days=x) for x in
                              range(0, (checkin_date_first_date - start_contract).days)]
            list_event = dict_info_output.get('listEvent', [])

            cnt_off = 0
            if len(date_generated) > 0:

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
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })
                    cnt_off = cnt_off + 1
            # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
            # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            dict_info_output['listEvent'] = list_event
            dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
            tuan_thu = dict_info_output['countOff'] + dict_info_output['countOnTime']
            percent_tuan_thu = tuan_thu / len(list_event)
            dict_info_output['percentAbide'] = round(percent_tuan_thu, 2)
            dict_info_output['percentNotAbide'] = 100 - round(percent_tuan_thu, 2)
            return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                 status=STATUS_CODE_SUCCESS)
        elif int(month_start_checkin) < int(month_input):

            # ngay ky hop dong ma ko di lam
            # start_contract = convert_str_to_date(str_start_contract)
            # % d / % m / % Y

            str_start_contract = "01/{}/{}".format(month_input, year_start_checkin)

            start_contract = convert_str_to_date(str_start_contract)
            date_generated = [start_contract + timedelta(days=x) for x in
                              range(0, (checkin_date_first_date - start_contract).days)]

            # print(len(date_generated) > 0)
            # print(checkin_date_first_date)
            # print(start_contract)
            list_event = dict_info_output.get('listEvent', [])
            cnt_off = 0
            if len(date_generated) > 0:

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
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })
                    cnt_off = cnt_off + 1
                # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            # list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
            list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
            # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
            dict_info_output['listEvent'] = list_event
            dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
            tuan_thu = dict_info_output['countOff'] + dict_info_output['countOnTime']
            percent_tuan_thu = tuan_thu / len(list_event)
            dict_info_output['percentAbide'] = round(percent_tuan_thu, 2)
            dict_info_output['percentNotAbide'] = 100 - round(percent_tuan_thu, 2)

            return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                 status=STATUS_CODE_SUCCESS)
        else:
            return response_data(data={'firstWorkdate': checkin_date_first},
                                 message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)


    else:
        dict_output = info_history_month_not_start_checkin(str_start_contract, year_input, month_input, device_name)
        dict_output.update({
            'firstWorkdate': str_start_contract
        })

        return response_data(data=dict_output, message=MESSAGE_API_NO_DATA,
                             status=STATUS_CODE_NO_DATA)


def history_checkin_on_month_past_year(year_input, month_input, emp_code, device_name, str_start_contract, checkin_date_first, checkin_date_first_date, fname):
    _date_input = str(year_input) + "-" + month_input
    queryset = EmpCheckin.objects.filter(emp_code=emp_code, checkin_date__startswith=_date_input).order_by(
        'checkin_date')

    serializer = EmpCheckinSerializer(queryset, many=True)
    list_data = serializer.data
    if len(list_data) > 0:
        dict_info_output = info_history_checkin_on_month(list_data, emp_code, device_name,
                                                         fname)
        dict_info_output.update({
            'firstWorkdate':  checkin_date_first
        })

        month_start_checkin = checkin_date_first.split("/")[1]
        year_start_checkin = checkin_date_first.split("/")[2]

        print(int(month_start_checkin) < int(month_input))


        if year_input >= year_start_checkin :
            if month_start_checkin == month_input:
                # ngay ky hop dong ma ko di lam
                str_start_contract = "01/{}/{}".format(month_start_checkin, year_start_checkin)
                start_contract = convert_str_to_date(str_start_contract)
                date_generated = [start_contract + timedelta(days=x) for x in
                                  range(0, (checkin_date_first_date - start_contract).days)]
                list_event = dict_info_output.get('listEvent', [])
                # print("===================++++")
                # print(list_event)
                cnt_off = 0
                if len(date_generated) > 0:

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
                            "deviceName": device_name,
                            "location": "",
                            "timeCheckin": "",
                            "numWorkday": 0
                        })
                        cnt_off = cnt_off + 1
                    # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
                # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                dict_info_output['listEvent'] = list_event
                dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
                tuan_thu = dict_info_output['countOff'] + dict_info_output['countOnTime']
                percent_tuan_thu = tuan_thu / len(list_event)
                dict_info_output['percentAbide'] = round(percent_tuan_thu, 2)
                dict_info_output['percentNotAbide'] = 100 - round(percent_tuan_thu, 2)
                return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                     status=STATUS_CODE_SUCCESS)

            elif int(month_start_checkin) < int(month_input):
                print("------------------------------")

                # ngay ky hop dong ma ko di lam
                # start_contract = convert_str_to_date(str_start_contract)
                # % d / % m / % Y

                str_start_contract = "01/{}/{}".format(month_input, year_start_checkin)

                start_contract = convert_str_to_date(str_start_contract)
                date_generated = [start_contract + timedelta(days=x) for x in
                                  range(0, (checkin_date_first_date - start_contract).days)]

                list_event = dict_info_output.get('listEvent', [])

                cnt_off = 0
                if len(date_generated) > 0:

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
                            "deviceName": device_name,
                            "location": "",
                            "timeCheckin": "",
                            "numWorkday": 0
                        })
                        cnt_off = cnt_off + 1
                    # list_event = preprocess_list_data_history_checkin_on_month(list_event, device_name)
                    # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                dict_info_output['listEvent'] = list_event

                list_event, cnt_off_1 = preprocess_list_data_history_checkin_on_month(list_event, device_name)
                # list_event = sorted(list_event, key=lambda k: convert_str_to_date(k['date']))
                dict_info_output['listEvent'] = list_event
                dict_info_output['countOff'] = dict_info_output['countOff'] + cnt_off + cnt_off_1
                tuan_thu = dict_info_output['countOff'] + dict_info_output['countOnTime']
                print("==================")
                print(dict_info_output['countOff'])
                print(dict_info_output['countOnTime'])
                percent_tuan_thu = tuan_thu / len(list_event)
                dict_info_output['percentAbide'] = round(percent_tuan_thu, 2)
                dict_info_output['percentNotAbide'] = 100 - round(percent_tuan_thu, 2)
                return response_data(data=dict_info_output, message=MESSAGE_API_SUCCESS,
                                     status=STATUS_CODE_SUCCESS)

                # =========================================

                # dict_info_output = info_history_checkin_on_month(list_data, emp_code, device_name, fname)
                # dict_info_output.update({
                #     'firstWorkdate': checkin_date_first
                # })

            else:
                return response_data(data={'firstWorkdate': checkin_date_first},
                                     message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
        else:
            return response_data(data={'firstWorkdate': checkin_date_first},
                                 message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)


    else:
        print("--------------")
        dict_output = info_history_month_not_start_checkin(str_start_contract, year_input, month_input, device_name)
        dict_output.update({
            'firstWorkdate': str_start_contract
        })

        return response_data(data=dict_output, message=MESSAGE_API_NO_DATA,
                             status=STATUS_CODE_NO_DATA)

def info_history_month_not_start_checkin_old(str_start_contract, year_input, mont_input, device_name):
    year_contract = str_start_contract.split("/")[2]
    month_contract = str_start_contract.split("/")[1]
    list_info_checkin = []
    print(int(year_contract) == int(year_input))
    if int(year_contract) == int(year_input):
        print(int(month_contract) == int(mont_input))
        if int(month_contract) == int(mont_input):
            time_contract = convert_str_to_date(str_start_contract)
            str_cuoi_thang = "31/{}/{}".format(mont_input, year_input)
            if not is_valid_date(31, int(mont_input), int(year_input)):
                str_cuoi_thang = "30/{}/{}".format(mont_input, year_input)
                if not is_valid_date(30,int(mont_input), int(year_input)):
                    str_cuoi_thang = "29/{}/{}".format(mont_input, year_input)
                    if not is_valid_date(29, int(mont_input), int(year_input)):
                        str_cuoi_thang = "28/{}/{}".format(mont_input, year_input)
                        # if not is_valid_date("29", mont_input, year_input):


            print(768)
            cuoi_thang = convert_str_to_date(str_cuoi_thang)
            date_generated = [time_contract + timedelta(days=x) for x in range(0, (cuoi_thang - time_contract).days + 1)]
            for k in date_generated:
                str_k = convert_date_export(k)
                print(773)
                thu = get_type_date_fr_str_date(str_k, '')
                if not is_null_or_empty(thu):
                    thu = thu.title()
                str_date = thu + ", Ngày " + str_k

                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": str_k,
                    "status": "off",
                    "deviceName": device_name,
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0
                })



            # xu ly tu ngày  ki den ngay cuoi thang
        elif int(month_contract) < int(mont_input):
            print("888888888888888888")
            for i in range(1, 32):
                _date = "{}/{}/{}".format(i,mont_input, year_input)
                if is_valid_date(i, int(mont_input), int(year_input)):
                    str_k = _date
                    thu = get_type_date_fr_str_date(str_k, '')
                    if not is_null_or_empty(thu):
                        thu = thu.title()
                    str_date = thu + ", Ngày " + str_k

                    list_info_checkin.append({
                        "dateDetail": str_date,
                        "date": str_k,
                        "status": "off",
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })



        else:
            # ko lam ji het
            pass


    elif  int(year_contract) < int(year_input):
        if int(month_contract) == int(mont_input):
            time_contract = convert_str_to_date(str_start_contract)
            str_cuoi_thang = "31/{}/{}".format(mont_input, year_input)
            if not is_valid_date(31, int(mont_input), int(year_input)):
                str_cuoi_thang = "30/{}/{}".format(mont_input, year_input)
                if not is_valid_date(30, int(mont_input), int(year_input)):
                    str_cuoi_thang = "29/{}/{}".format(mont_input, year_input)
                    if not is_valid_date(29, int(mont_input), int(year_input)):
                        str_cuoi_thang = "28/{}/{}".format(mont_input, year_input)
                        # if not is_valid_date("29", mont_input, year_input):

            print(768)
            cuoi_thang = convert_str_to_date(str_cuoi_thang)
            date_generated = [time_contract + timedelta(days=x) for x in
                              range(0, (cuoi_thang - time_contract).days + 1)]
            for k in date_generated:
                str_k = convert_date_export(k)
                print(773)
                thu = get_type_date_fr_str_date(str_k, '')
                if not is_null_or_empty(thu):
                    thu = thu.title()
                str_date = thu + ", Ngày " + str_k

                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": str_k,
                    "status": "off",
                    "deviceName": '',
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0
                })

            # xu ly tu ngày  ki den ngay cuoi thang
        elif int(month_contract) < int(mont_input):
            print("888888888888888888")
            for i in range(1, 32):
                _date = "{}/{}/{}".format(i, mont_input, year_input)
                if is_valid_date(i, int(mont_input), int(year_input)):
                    str_k = _date
                    thu = get_type_date_fr_str_date(str_k, '')
                    if not is_null_or_empty(thu):
                        thu = thu.title()
                    str_date = thu + ", Ngày " + str_k

                    list_info_checkin.append({
                        "dateDetail": str_date,
                        "date": str_k,
                        "status": "off",
                        "deviceName": device_name,
                        "location": "",
                        "timeCheckin": "",
                        "numWorkday": 0
                    })



        else:
            # ko lam ji het
            pass

    else:
        return {}

    dict_info_output = {
        "countLate": 0,
        "countOnTime": 0,
        "countOff": len(list_info_checkin),
        "countWorkday": 0,
        'percentAbide': 100,
        'percentNotAbide': 0,
        "listEvent": list_info_checkin

    }
    return dict_info_output


def info_history_month_not_start_checkin(str_start_contract, year_input, mont_input):
    list_info_checkin = []
    # trương hop khong co lich truc trong db

    day_contract = str_start_contract.split("/")[0]
    # month_contract = str_start_contract.split("/")[1]
    # year_contract = str_start_contract.split("/")[2]

    str_day_input = "{}/{}/{}".format(day_contract, mont_input, year_input)
    day_input = convert_str_to_date(str_day_input)

    start_contract = convert_str_to_date(str_start_contract)

    if day_input == start_contract:
        time_contract = convert_str_to_date(str_start_contract)
        str_cuoi_thang = "31/{}/{}".format(mont_input, year_input)
        if not is_valid_date(31, int(mont_input), int(year_input)):
            str_cuoi_thang = "30/{}/{}".format(mont_input, year_input)
            if not is_valid_date(30, int(mont_input), int(year_input)):
                str_cuoi_thang = "29/{}/{}".format(mont_input, year_input)
                if not is_valid_date(29, int(mont_input), int(year_input)):
                    str_cuoi_thang = "28/{}/{}".format(mont_input, year_input)
                    # if not is_valid_date("29", mont_input, year_input):

        # print(768)
        cuoi_thang = convert_str_to_date(str_cuoi_thang)
        date_generated = [time_contract + timedelta(days=x) for x in range(0, (cuoi_thang - time_contract).days + 1)]
        for k in date_generated:
            str_k = convert_date_export(k)
            # print(773)
            thu = get_type_date_fr_str_date(str_k, '')
            if not is_null_or_empty(thu):
                thu = thu.title()
            str_date = thu + ", Ngày " + str_k

            list_info_checkin.append({
                "dateDetail": str_date,
                "date": str_k,
                "status": "off",
                "deviceName": '',
                "location": "",
                "timeCheckin": "",
                "numWorkday": 0.0
            })
    elif day_input > start_contract:
        for i in range(1, 32):
            _date = "{}/{}/{}".format(i, mont_input, year_input)
            if is_valid_date(i, int(mont_input), int(year_input)):
                str_k = _date
                thu = get_type_date_fr_str_date(str_k, '')
                if not is_null_or_empty(thu):
                    thu = thu.title()
                str_date = thu + ", Ngày " + str_k

                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": str_k,
                    "status": "off",
                    "deviceName": '',
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0.0
                })

    return list_info_checkin

def info_history_month_not_start_checkin_month_now(str_start_contract, year_input, mont_input):
    list_info_checkin = []
    # trương hop khong co lich truc trong db

    day_contract = str_start_contract.split("/")[0]
    # month_contract = str_start_contract.split("/")[1]
    # year_contract = str_start_contract.split("/")[2]

    str_day_input = "{}/{}/{}".format(day_contract, mont_input, year_input)
    day_input = convert_str_to_date(str_day_input)

    start_contract = convert_str_to_date(str_start_contract)

    print(44444)
    print(day_input == start_contract)
    print(day_input)
    print(start_contract)

    if day_input == start_contract:
        time_contract = convert_str_to_date(str_start_contract)
        str_cuoi_thang = get_str_date_now_export()
        # str_cuoi_thang = "31/{}/{}".format(mont_input, year_input)
        # if not is_valid_date(31, int(mont_input), int(year_input)):
        #     str_cuoi_thang = "30/{}/{}".format(mont_input, year_input)
        #     if not is_valid_date(30, int(mont_input), int(year_input)):
        #         str_cuoi_thang = "29/{}/{}".format(mont_input, year_input)
        #         if not is_valid_date(29, int(mont_input), int(year_input)):
        #             str_cuoi_thang = "28/{}/{}".format(mont_input, year_input)

        # print(768)
        cuoi_thang = convert_str_to_date(str_cuoi_thang)
        print(cuoi_thang)
        date_generated = [time_contract + timedelta(days=x) for x in range(0, (cuoi_thang - time_contract).days + 1)]
        for k in date_generated:
            str_k = convert_date_export(k)
            # print(773)
            thu = get_type_date_fr_str_date(str_k, '')
            if not is_null_or_empty(thu):
                thu = thu.title()
            str_date = thu + ", Ngày " + str_k

            list_info_checkin.append({
                "dateDetail": str_date,
                "date": str_k,
                "status": "off",
                "deviceName": '',
                "location": "",
                "timeCheckin": "",
                "numWorkday": 0.0
            })
    elif day_input > start_contract:
        str_date_now = get_str_date_now_export()
        _date_now = str_date_now.split("/")[0]

        for i in range(1, int(_date_now) + 1):
            _date = "{}/{}/{}".format(i, mont_input, year_input)
            if is_valid_date(i, int(mont_input), int(year_input)):
                str_k = _date
                thu = get_type_date_fr_str_date(str_k, '')
                if not is_null_or_empty(thu):
                    thu = thu.title()
                str_date = thu + ", Ngày " + str_k

                list_info_checkin.append({
                    "dateDetail": str_date,
                    "date": str_k,
                    "status": "off",
                    "deviceName": '',
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0.0
                })

    return list_info_checkin


def pre_process_list_info_checkin(list_data, month_input, year_input, past):
    list_new = list_data.copy()

    # str_max_date = list_data[0]['date']
    # str_min_date = list_data[0]['date']
    # max_date = convert_str_to_date(str_max_date)
    # min_date = convert_str_to_date(str_min_date)

    if past:
        str_min_date = "01/{}/{}".format(month_input, year_input)
        # min_date = convert_str_to_date(str_min_date)

        str_max_date = "31/{}/{}".format(month_input, year_input)
        if not is_valid_date(31, int(month_input), int(year_input)):
            str_max_date = "30/{}/{}".format(month_input, year_input)
            if not is_valid_date(30, int(month_input), int(year_input)):
                str_max_date = "29/{}/{}".format(month_input, year_input)
                if not is_valid_date(29, int(month_input), int(year_input)):
                    str_max_date = "28/{}/{}".format(month_input, year_input)
                    # if not is_valid_date("29", mont_input, year_input):
    else:
        str_min_date = "01/{}/{}".format(month_input, year_input)
        str_max_date = get_str_date_now_export()


    max_date = convert_str_to_date(str_max_date)
    min_date = convert_str_to_date(str_min_date)


    device_name = list_data[0]['deviceName']

    list_date_data = []
    cnt_off = 0
    if len(list_data) > 0:
        for i in list_data:
            str_date = i['date']
            list_date_data.append(str_date)
            # _date = convert_str_to_date(str_date)
            # if _date > max_date:
            #     max_date = _date
            #
            # if _date < min_date:
            #     min_date = _date
        if past:
            date_generated = [min_date + timedelta(days=x) for x in
                              range(0, (max_date - min_date).days + 1)]
        else:
            date_generated = [min_date + timedelta(days=x) for x in
                              range(0, (max_date - min_date).days )]
        list_str_date_generate = []

        for k in date_generated:
            str_k = convert_date_export(k)
            list_str_date_generate.append(str_k)

        for i_date in list_str_date_generate:
            if i_date not in list_date_data:

                thu = get_type_date_fr_str_date(i_date, '')
                if not is_null_or_empty(thu):
                    thu = thu.title()
                str_date = thu + ", Ngày " + i_date
                list_new.append({
                    "dateDetail": str_date,
                    "date": i_date,
                    "status": "off",
                    "deviceName": '',
                    "location": "",
                    "timeCheckin": "",
                    "numWorkday": 0.0
                })
                cnt_off = cnt_off + 1






    return list_new, cnt_off

def cron_update_coordinate(data, str_date_now_db, str_time_now, res_time, branch_process):
    # queryset = EmpCheckin.objects.filter(checkin_date=str_date_now_db).exclude(checkin_success="OK",
    #                                                                            team_name__in=tuple(LIST_BLOCK))
    # serializer = EmpCheckinSerializer(queryset, many=True)
    # data = serializer.data
    print("===================={}=======================".format(branch_process))
    # print(data)
    list_mbn = []
    # list_emp_code = []
    list_PNC = []
    list_block_PNC = []
    status_PNC = 0
    status_block_PNC = 0

    list_afternoon = []
    status_afternoon = []
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
            host="https://trackingapi.fpt.vn/",
            func="api/getLocationUsers",
            method="POST",
            data={"EmpID": list_mbn}
        )
        dataApi = json.loads(response)
        # print("=====================================BAN API THANH CONG==============================")
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
            if result_data is not None:
                if len(result_data) > 0:
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

                                    # xu ly vi tri

                                    dict_position = calculcate_distance_for_official_emp(emp_coordinate=emp_coordinate,
                                                                                         block_center=block_center,
                                                                                         block_distance=block_distance,
                                                                                         office_center=office_center,
                                                                                         block_name=block_name)
                                    status_position = dict_position.get("checkin")
                                    add_checkin = dict_position.get('location')

                                    if status_position is not None:
                                        if status_position == "NOTOK":
                                            pass
                                        else:
                                            dict_data_workday = compute_workday_for_offcial_workday(team_name, str_time_now,
                                                                                                    ca, add_checkin)
                                            status = dict_data_workday['status']
                                            check_in = dict_data_workday['check_in']
                                            workday_convert = status

                                            if ca == "C":
                                                status_afternoon = status
                                                list_afternoon.append(emp_code)
                                            else:
                                                if add_checkin == "BLOCK":
                                                    status_block_PNC = status
                                                    list_block_PNC.append(emp_code)
                                                else:
                                                    list_PNC.append(emp_code)
                                                    status_PNC = status



                                            # EmpCheckin.objects.filter(emp_code=emp_code, checkin_date=str_date_now_db).update(
                                            #     checkin_success=check_in,
                                            #     workday_factor=status,
                                            #     workday_convert=workday_convert,
                                            #     checkin_time=res_time,
                                            #     location=add_checkin, count_response=99)

                                            date_now = get_current_date()
                                            str_time_now_new = date_now.strftime('%d/%m/%Y')

                                            # device_token_emp = dict_data_token.get(emp_code)
                                            # if not is_null_or_empty(device_token_emp):
                                            params = {
                                                # "deviceToken": device_token_emp,
                                                "emp_code": emp_code,
                                                "title": "Điểm danh thành công",
                                                "body": "Bạn đã điểm danh thành công vào lúc {} ngày {}".format(
                                                    res_time, str_time_now_new),
                                                "topic_type": "checkin",
                                                "notifyActionType": "go_to_screen",
                                                "notifyDataAction": "/check-in-history",
                                                "popupDetailActionType": "go_to_screen",
                                                "popupDetailDataAction": "/check-in-history",

                                                # "navigate": "/historyCheckIn"

                                            }
                                            # print(params)
                                            # msg = call_api_noti_success_checkin(params)
                                            # print("-----------------------BAN NOT -------------------------")
                                            # print(msg)
                                            list_noti.append(params)
                                    else:
                                        print("=================CO LOI TOA DO==============")
                                        print(i_data)



                                else:
                                    content_output = "Bạn đã điểm danh"
                            else:
                                device_name_acc = dict_data_device_name.get(emp_code)
                                save_db_shift_off_new(history_coordiante, res_time, emp_coordinate, emp_code,
                                                      str_date_now_db, block_distance, block_center, office_center,
                                                      block_name, team_name, str_time_now, ca, device_name_acc)

                    if len(list_PNC) > 0:
                        EmpCheckin.objects.filter(emp_code__in=tuple(list_PNC), checkin_date=str_date_now_db).update(
                            checkin_success="OK",
                            workday_factor=status_PNC,
                            workday_convert=status_PNC,
                            checkin_time=res_time, count_response=99,location="VP")

                    if len(list_block_PNC) > 0 :
                        EmpCheckin.objects.filter(emp_code__in=tuple(list_block_PNC), checkin_date=str_date_now_db).update(
                            checkin_success="OK",
                            workday_factor=status_block_PNC,
                            workday_convert=status_block_PNC,
                            checkin_time=res_time, count_response=99,location="BLOCK" )

                    if len(list_afternoon) > 0:
                        EmpCheckin.objects.filter(emp_code__in=tuple(list_afternoon),
                                                  checkin_date=str_date_now_db).update(
                            checkin_success="OK",
                            workday_factor=status_afternoon,
                            workday_convert=status_afternoon,
                            checkin_time=res_time, count_response=99, location="BLOCK")



                if len(list_noti) > 0:
                    params = {
                        "data": list_noti
                    }
                    msg = call_api_change_shift(params=params)
                    print("------------------BAN NOTI------------------------")
                    # print(msg)
                # return response_data("serializer.data")
            else:
                # return response_data("Không lấy được data")
                print("KHONG LAY DUOC DATA ")
        else:
            # return response_data(data='loi khi ban api tracking', message="", status=0)
            print("loi khi ban api tracking")
    else:
        print("khong co thong tin cho diem danh tu dong PNC")
        # return response_data(data='khong co thong tin', message="", status=0)


def insert_response(str_time_now,emp_code,response_content,response_id,coordinate,checkin_id, device_id):
    try:
        emp_response = EmpResponse()
        emp_response.update_time = str_time_now
        emp_response.emp_code = emp_code
        emp_response.response = response_content
        emp_response.response_id = response_id
        emp_response.coordinate = coordinate
        emp_response.checkin_id = checkin_id
        emp_response.device_id = device_id
        save_response = emp_response.save()
    except Exception as ex:
        print("===================insert_response===========")
        print(ex)







