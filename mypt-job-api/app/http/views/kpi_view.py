import json
from ...core.helpers.utils import api_save_log
import calendar
from numpy import empty

from ..models.kpi import Kpi
from ..models.job_configs import JobConfigs
from ..models.kpi_info import KpiInfo
from ..models.kpi_task import KpiTask
from ...core.helpers import auth_session_handler as authSessionHandler
from ..serializers.job_configs_serializer import JobConfigsSerializer
from ...core.helpers.global_variable import *
from ...core.helpers.my_datetime import *
from ...core.helpers.response import *
from ...core.helpers.helper import *
from rest_framework.viewsets import ViewSet
from ...core.entities.redis_service import RedisService
import ast
from django.db.models import Q
from datetime import datetime, timedelta
from django.db import connection
from datetime import datetime, date
import redis
from django.conf import settings as project_settings



def get_kpi_month(**kwargs):
    typeKpi = kwargs.pop('type', None)
    dateMonth = kwargs.pop('date', None)
    empCode = kwargs.pop('emp_code', None)

    month = 1
    overPass = 100

    dateConvert = convert_string_date(dateMonth, month_YEAR)

    listMonth = []
    result = {}

    conKpi = KpiInfo.objects.all()
    for infoKpi in conKpi:
        if infoKpi.kpi_type == typeKpi:
            data = json.loads(infoKpi.kpi_value)
            # if typeKpi in ['kh2cl', 'kh3cl', 'clps_7n']:
            #     result['infoTarget'] = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
            #         infoKpi.year) + " là " + start_tag_b_html + "<= " + str(format_number(infoKpi.target)) + "%" + end_tag_b_html + end_tag_div_html
            # else:
            #     result['infoTarget'] = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
            #         infoKpi.year) + " là " + start_tag_b_html + ">= " + str(format_number(infoKpi.target)) + "%" + end_tag_b_html + end_tag_div_html
            # listText = infoKpi.description.split(" = ")
            # result['desKpi'] = start_tag_div_html + start_tag_b_html + "•  " + listText[0] + " = " + end_tag_b_html + listText[1][:-5] +
            # start_tag_b_html + "x 100" + end_tag_b_html + end_tag_div_html
            result['desKpi'] = ""
            result['infoTarget'] = ""
            result['titlePercentPass'] = data['titlePercentPass']
            result['titlePercentFail'] = data['titlePercentFail']
            result['titleCountPass'] = data['titleCountPass']
            result['titleCountFail'] = data['titleCountFail']
            result['titleInformation'] = data['titleInformation']
            if typeKpi in ['kpi_ontime', 'kh2cl', 'kh3cl', 'clps_7n']:
                result['titleInformation'] = data['titleInformation'] + " trong tháng"

    while month <= dateConvert.month:
        isPass = True
        kpiDate = str(month) + "/" + str(dateConvert.year)
        queryset = KpiTask.objects.filter(kpi_date__month=month, kpi_date__year=dateConvert.year, emp_code=empCode)
        kpiCon = KpiInfo.objects.filter(kpi_type=typeKpi)
        if queryset:
            count_ontime_tk_bt = 0
            count_late_tk_bt = 0
            count_shift_complete_sla = 0
            count_shift_sla = 0
            count_2cl = 0
            count_3cl = 0
            count_clps7n = 0
            count_customer_cl = 0
            for data in queryset:
                # tổng số ca đúng hẹn - trễ hẹn (TK + BT)
                count_ontime_tk_bt += data.ontime_tk + data.ontime_bt
                count_late_tk_bt += data.late_tk + data.late_bt
                # tổng số ca sla (TK + BT)
                count_shift_complete_sla += data.count_shift_complete_sla_tk + data.count_shift_complete_sla_bt
                count_shift_sla += data.count_shift_sla_tk + data.count_shift_sla_bt
                # tổng số ca checklist2 - checklist3
                count_2cl += data.count_cl2
                count_3cl += data.count_cl3
                # tổng sl KH có check
                count_customer_cl += data.customer_cl
                count_clps7n += data.count_cl7n_bt + data.count_cl7n_tk

            for con in kpiCon:
                percentPass = 0
                percentFail = 0
                if con.kpi_type == typeKpi:
                    if typeKpi == "kpi_ontime":
                        countPass = count_ontime_tk_bt
                        countFail = count_late_tk_bt
                        total = countPass + countFail
                        if total != 0:
                            percentPass = float('{:.2f}'.format((countPass / total) * 100))
                            if percentPass > overPass:
                                percentPass = overPass
                            percentFail = float('{:.2f}'.format(100 - percentPass))
                        if percentPass < con.target:
                            isPass = False

                    if typeKpi == "kpi_sla":
                        countPass = count_shift_complete_sla
                        total = count_shift_sla
                        countFail = total - countPass
                        if total != 0:
                            percentPass = float('{:.2f}'.format((countPass / total) * 100))
                            if percentPass > overPass:
                                percentPass = overPass
                            percentFail = float('{:.2f}'.format(100 - percentPass))
                        if percentPass < con.target:
                            isPass = False

                    if typeKpi == "kh2cl":
                        countFail = count_2cl
                        total = count_customer_cl
                        countPass = total - countFail
                        if countPass < 0:
                            countPass = 0
                        if total == 0:
                            total += countFail
                        if total != 0:
                            percentFail = float('{:.2f}'.format((countFail / total) * 100))
                            if percentFail > overPass:
                                percentFail = overPass
                            percentPass = float('{:.2f}'.format(100 - percentFail))
                        if percentFail > con.target:
                            isPass = False

                    if typeKpi == "kh3cl":
                        countFail = count_3cl
                        total = count_customer_cl
                        countPass = total - countFail
                        if countPass < 0:
                            countPass = 0
                        if total == 0:
                            total += countFail
                        if total != 0:
                            percentFail = float('{:.2f}'.format((countFail / total) * 100))
                            if percentFail > overPass:
                                percentFail = overPass
                            percentPass = float('{:.2f}'.format(100 - percentFail))
                        if percentFail > con.target:
                            isPass = False

                    if typeKpi == "clps_7n":
                        countFail = count_clps7n
                        total = count_ontime_tk_bt + count_late_tk_bt
                        countPass = total - countFail
                        if countPass < 0:
                            countPass = 0
                        if total != 0:
                            percentFail = float('{:.2f}'.format((countFail / total) * 100))
                            if percentFail > overPass:
                                percentFail = overPass
                            percentPass = float('{:.2f}'.format(100 - percentFail))
                        if percentFail > con.target:
                            isPass = False

                    listMonth.append({
                        "order": month,
                        "percentPass": format_number(percentPass),
                        "percentFail": format_number(percentFail),
                        "countPass": countPass,
                        "countFail": countFail,
                        "total": total,
                        "isPass": isPass,
                        "kpiDate": kpiDate
                    })
        else:
            kpi = {
                "order": month,
                "percentPass": 0,
                "percentFail": 0,
                "countPass": 0,
                "countFail": 0,
                "total": 0,
                "isPass": True,
                "kpiDate": kpiDate
            }
            listMonth.append(kpi)
        month += 1

    result['listChart'] = listMonth
    return result


def get_kpi_month_info(**kwargs):
    typeKpi = kwargs.pop('type', None)
    dateMonth = kwargs.pop('date', None)
    empCode = kwargs.pop('emp_code', None)

    listContract = []
    listTitle = ["", "", ""]
    result = {}

    dateConvert = convert_string_date(dateMonth, month_YEAR)

    if typeKpi == 'kpi_sla':
        listTitle = ["Số hợp đồng", "Thời gian tích hẹn", "Thời gian hoàn tất"]
        queryset = Kpi.objects.filter(kpi_date__month=dateConvert.month, kpi_date__year=dateConvert.year,
                                      emp_code=empCode, kpi_type__contains='sla')
        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
            timeChecklist = "N/A"
            if data.time_start_cl1:
                timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""
            if data.kpi_type == 'sla_tk':
                typeContract = "tk"
            if data.kpi_type == 'sla_bt':
                typeContract = "bt"

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'kh2cl':
        listTitle = ["Số hợp đồng", "Thời gian hoàn tất CL0", "Thời gian phát sinh CL1"]
        queryset = Kpi.objects.filter(kpi_date__month=dateConvert.month, kpi_date__year=dateConvert.year,
                                      emp_code=empCode, kpi_type__contains=typeKpi)
        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
            timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'kh3cl':
        listTitle = ["Số hợp đồng", "Thời gian hoàn tất CL1", "Thời gian phát sinh CL2"]
        queryset = Kpi.objects.filter(kpi_date__month=dateConvert.month, kpi_date__year=dateConvert.year,
                                      emp_code=empCode, kpi_type__contains=typeKpi)
        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete_cl1.strftime("%d/%m/%Y %H:%M:%S")
            timeChecklist = data.time_start_cl2.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'clps_7n':
        queryset = Kpi.objects.filter(kpi_date__month=dateConvert.month, kpi_date__year=dateConvert.year,
                                      emp_code=empCode, kpi_type__contains='cl_7n')
        for data in queryset:
            nameContract = data.contract
            timeComplete = ""
            timeChecklist = ""
            typeContract = ""
            if data.kpi_type == 'cl_7n_tk':
                listTitle = ["Số hợp đồng", "Thời gian hoàn tất PTC", "Thời gian phát sinh CL"]
                timeComplete = data.time_complete_ptc.strftime("%d/%m/%Y %H:%M:%S")
                timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
                typeContract = "tk"
            if data.kpi_type == 'cl_7n_bt':
                listTitle = ["Số hợp đồng", "Thời gian hoàn tất CL", "Thời gian phát sinh CL"]
                timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
                timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
                typeContract = "bt"

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'kpi_ontime':
        listTitle = ["Số hợp đồng", "Thời gian hoàn tất"]
        queryset = Kpi.objects.filter(kpi_date__month=dateConvert.month, kpi_date__year=dateConvert.year,
                                      emp_code=empCode, kpi_type__contains='kpi', status='late')

        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""
            if data.kpi_type == 'kpi_tk':
                typeContract = "tk"
            if data.kpi_type == 'kpi_bt':
                typeContract = "bt"

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "type": typeContract
            })

    result['listContract'] = listContract
    result['listTitle'] = listTitle

    return result


def get_kpi_day(**kwargs):
    typeKpi = kwargs.pop('type', None)
    dateDay = kwargs.pop('date', None)
    empCode = kwargs.pop('emp_code', None)
    overPass = 100
    target = 0

    dateConvert = convert_string_date(dateDay, day_month_YEAR)

    day = 1
    dictDays = {}
    listDays = []
    result = {}

    kpiCon = KpiInfo.objects.filter(kpi_type=typeKpi)
    for infoKpi in kpiCon:
        data = json.loads(infoKpi.kpi_value)
        # if typeKpi in ['kh2cl', 'kh3cl', 'clps_7n']:
        #     result['infoTarget'] = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
        #         infoKpi.year) + " là " + start_tag_b_html + "<= " + str(format_number(infoKpi.target)) + "%" + end_tag_b_html + end_tag_div_html
        # else:
        #     result['infoTarget'] = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
        #         infoKpi.year) + " là " + start_tag_b_html + ">= " + str(format_number(infoKpi.target)) + "%" + end_tag_b_html + end_tag_div_html
        # listText = infoKpi.description.split(" = ")
        # result['desKpi'] = start_tag_div_html + start_tag_b_html + "•  " + listText[0] + " = " + end_tag_b_html + listText[1][:-5] + start_tag_b_html + "x 100" + end_tag_b_html + end_tag_div_html
        result['desKpi'] = ""
        result['infoTarget'] = ""
        result['titlePercentPass'] = data['titlePercentPass']
        result['titlePercentFail'] = data['titlePercentFail']
        result['titleCountPass'] = data['titleCountPass']
        result['titleCountFail'] = data['titleCountFail']
        result['titleInformation'] = data['titleInformation']
        if typeKpi in ['kpi_ontime', 'kh2cl', 'kh3cl', 'clps_7n']:
            result['titleInformation'] = data['titleInformation'] + " trong ngày"
        target = infoKpi.target

    queryset = KpiTask.objects.filter(kpi_date__month=dateConvert.month, kpi_date__year=dateConvert.year,
                                      emp_code=empCode).order_by('kpi_date')

    # khởi tạo list dictionary
    while day <= dateConvert.day:
        dictDays[day] = None
        day += 1

    for data in queryset:
        day = data.kpi_date.day
        dictDays[day] = data

    count_2cl = 0
    count_3cl = 0
    count_customer_cl = 0
    count_ontime_late = 0
    count_clps7n = 0
    for key, value in dictDays.items():
        countPass = 0
        countFail = 0
        percentPass = 0
        percentFail = 0
        isPass = True
        kpiDate = str(key) + "/" + str(dateConvert.month) + "/" + str(dateConvert.year)
        if value:
            # tổng số ca đúng hẹn - trễ hẹn (TK + BT)
            count_ontime_tk_bt = value.ontime_tk + value.ontime_bt
            count_late_tk_bt = value.late_tk + value.late_bt
            count_ontime_late += count_late_tk_bt + count_ontime_tk_bt
            # tổng số ca sla (TK + BT)
            count_shift_complete_sla = value.count_shift_complete_sla_tk + value.count_shift_complete_sla_bt
            count_shift_sla = value.count_shift_sla_tk + value.count_shift_sla_bt
            # tổng số ca checklist2 - checklist3
            count_2cl += value.count_cl2
            count_3cl += value.count_cl3
            # tổng sl KH có check
            count_customer_cl += value.customer_cl
            count_clps7n += value.count_cl7n_bt + value.count_cl7n_tk

            if typeKpi == 'kpi_ontime':
                countPass = count_ontime_tk_bt
                countFail = count_late_tk_bt
                total = countPass + countFail
                if total != 0:
                    percentPass = float('{:.2f}'.format((countPass / total) * 100))
                    if percentPass > overPass:
                        percentPass = overPass
                    percentFail = float('{:.2f}'.format(100 - percentPass))
                    if percentPass < target:
                        isPass = False

            if typeKpi == 'kpi_sla':
                countPass = count_shift_complete_sla
                total = count_shift_sla
                countFail = total - countPass
                if total != 0:
                    percentPass = float('{:.2f}'.format((countPass / total) * 100))
                    if percentPass > overPass:
                        percentPass = overPass
                    percentFail = float('{:.2f}'.format(100 - percentPass))
                    if percentPass < target:
                        isPass = False

            if typeKpi == 'kh2cl':
                countFail = count_2cl
                total = count_customer_cl
                countPass = total - countFail
                if countPass < 0:
                    countPass = 0
                if total != 0:
                    percentFail = float('{:.2f}'.format((countFail / total) * 100))
                    if percentFail > overPass:
                        percentFail = overPass
                    percentPass = float('{:.2f}'.format(100 - percentFail))
                    if percentFail > target:
                        isPass = False

            if typeKpi == 'kh3cl':
                countFail = count_3cl
                total = count_customer_cl
                countPass = total - countFail
                if countPass < 0:
                    countPass = 0
                if total != 0:
                    percentFail = float('{:.2f}'.format((countFail / total) * 100))
                    if percentFail > overPass:
                        percentFail = overPass
                    percentPass = float('{:.2f}'.format(100 - percentFail))
                    if percentFail > target:
                        isPass = False

            if typeKpi == 'clps_7n':
                countFail = count_clps7n
                total = count_ontime_late
                countPass = total - countFail
                if countPass < 0:
                    countPass = 0
                if total != 0:
                    percentFail = float('{:.2f}'.format((countFail / total) * 100))
                    if percentFail > overPass:
                        percentFail = overPass
                    percentPass = float('{:.2f}'.format(100 - percentFail))
                    if percentFail > target:
                        isPass = False

            listDays.append({
                "order": key,
                "percentPass": format_number(percentPass),
                "percentFail": format_number(percentFail),
                "countPass": countPass,
                "countFail": countFail,
                "total": total,
                "isPass": isPass,
                "kpiDate": kpiDate
            })
        else:
            if typeKpi == 'kh2cl':
                countFail = count_2cl
                total = count_customer_cl
                countPass = total - countFail
                if countPass < 0:
                    countPass = 0
                listDays.append({
                    "order": key,
                    "percentPass": 0,
                    "percentFail": 0,
                    "countPass": countPass,
                    "countFail": countFail,
                    "total": total,
                    "isPass": True,
                    "kpiDate": kpiDate
                })
            elif typeKpi == 'kh3cl':
                countFail = count_3cl
                total = count_customer_cl
                countPass = total - countFail
                if countPass < 0:
                    countPass = 0
                listDays.append({
                    "order": key,
                    "percentPass": 0,
                    "percentFail": 0,
                    "countPass": countPass,
                    "countFail": countFail,
                    "total": total,
                    "isPass": True,
                    "kpiDate": kpiDate
                })

            elif typeKpi == 'clps_7n':
                countFail = count_clps7n
                total = count_ontime_late
                countPass = total - countFail
                if countPass < 0:
                    countPass = 0
                listDays.append({
                    "order": key,
                    "percentPass": 0,
                    "percentFail": 0,
                    "countPass": countPass,
                    "countFail": countFail,
                    "total": total,
                    "isPass": True,
                    "kpiDate": kpiDate
                })
            else:
                listDays.append({
                    "order": key,
                    "percentPass": 0,
                    "percentFail": 0,
                    "countPass": 0,
                    "countFail": 0,
                    "total": 0,
                    "isPass": True,
                    "kpiDate": kpiDate
                })

    result['listChart'] = listDays
    return result


def get_kpi_day_info(**kwargs):
    typeKpi = kwargs.pop('type', None)
    dateDay = kwargs.pop('date', None)
    empCode = kwargs.pop('emp_code', None)

    listContract = []
    listTitle = []
    result = {

    }

    dateConvert = convert_string_date(dateDay, day_month_YEAR)

    if typeKpi == 'kpi_sla':
        listTitle = ["Số hợp đồng", "Thời gian tích hẹn", "Thời gian hoàn tất"]
        queryset = Kpi.objects.filter(kpi_date=dateConvert, emp_code=empCode, kpi_type__contains='sla')
        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
            timeChecklist = "N/A"
            if data.time_start_cl1:
                timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""
            if data.kpi_type == 'sla_tk':
                typeContract = "tk"
            if data.kpi_type == 'sla_bt':
                typeContract = "bt"

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'kh2cl':
        listTitle = ["Số hợp đồng", "Thời gian hoàn tất CL0", "Thời gian phát sinh CL1"]
        queryset = Kpi.objects.filter(kpi_date=dateConvert, emp_code=empCode, kpi_type__contains=typeKpi)
        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
            timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'kh3cl':
        listTitle = ["Số hợp đồng", "Thời gian hoàn tất CL1", "Thời gian phát sinh CL2"]
        queryset = Kpi.objects.filter(kpi_date=dateConvert, emp_code=empCode, kpi_type__contains=typeKpi)
        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete_cl1.strftime("%d/%m/%Y %H:%M:%S")
            timeChecklist = data.time_start_cl2.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'clps_7n':
        queryset = Kpi.objects.filter(kpi_date=dateConvert, emp_code=empCode, kpi_type__contains='cl_7n')
        for data in queryset:
            nameContract = data.contract
            timeComplete = ""
            timeChecklist = ""
            typeContract = ""
            if data.kpi_type == 'cl_7n_tk':
                listTitle = ["Số hợp đồng", "Thời gian hoàn tất PTC", "Thời gian phát sinh CL"]
                timeComplete = data.time_complete_ptc.strftime("%d/%m/%Y %H:%M:%S")
                timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
                typeContract = "tk"
            if data.kpi_type == 'cl_7n_bt':
                listTitle = ["Số hợp đồng", "Thời gian hoàn tất CL0", "Thời gian phát sinh CL1"]
                timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
                timeChecklist = data.time_start_cl1.strftime("%d/%m/%Y %H:%M:%S")
                typeContract = "bt"

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "timeChecklist": timeChecklist,
                "type": typeContract
            })

    if typeKpi == 'kpi_ontime':
        listTitle = ["Số hợp đồng", "Thời gian hoàn tất"]
        queryset = Kpi.objects.filter(kpi_date=dateConvert, emp_code=empCode,
                                      kpi_type__contains='kpi', status='late')

        for data in queryset:
            nameContract = data.contract
            timeComplete = data.time_complete.strftime("%d/%m/%Y %H:%M:%S")
            typeContract = ""
            if data.kpi_type == 'kpi_tk':
                typeContract = "tk"
            if data.kpi_type == 'kpi_bt':
                typeContract = "bt"

            listContract.append({
                "contract": nameContract,
                "timeComplete": timeComplete,
                "type": typeContract
            })

    result['listContract'] = listContract
    result['listTitle'] = listTitle

    return result


def get_csat_average_result(**kwargs):
    startDay = kwargs.pop('start', None)
    endDay = kwargs.pop('end', None)
    account = kwargs.pop('account', None)

    if startDay == endDay:
        res = calendar.monthrange(endDay.year, endDay.month)
        day = res[1]
        endDay = date(endDay.year, endDay.month, day)

    msg = {
        "DateStart": startDay,
        "DateEnd": endDay,
        "AccountEMP": account
    }

    url = "https://survey.fpt.vn/api/v1/get-average-point-emp"
    dict_tmp = {}
    try:
        res = requests.post(url=url, data=msg)
        data = res.json()
        dict_tmp["csat_nv"] = data['detail']['Staff']
        dict_tmp["csat_dv"] = data['detail']['Service']
    except Exception as ex:
        print("loi khi lay data >> {}: {} khong cho ket qua json  ".format(ex, url))
    return dict_tmp


def get_detail_point_emp_csat(**kwargs):
    startDay = kwargs.pop('start', None)
    endDay = kwargs.pop('end', None)
    account = kwargs.pop('account', None)

    msg = {
        "DateStart": startDay,
        "DateEnd": endDay,
        "AccountEMP": account,
    }

    url = "https://survey.fpt.vn/api/v1/get-detail-point-emp"
    dict_tmp = {}

    proxies = {
        "http": None,
        "https": None,
    }

    try:
        res = requests.post(url=url, data=msg, proxies=proxies)
        data = res.json()
        dict_tmp = data['detail']
    except Exception as ex:
        print("loi khi lay data >> {}: {} khong cho ket qua json  ".format(ex, url))
    return dict_tmp


def get_detail_point_emp_csat_month(**kwargs):
    startDay = kwargs.pop('start', None)
    endDay = kwargs.pop('end', None)
    account = kwargs.pop('account', None)

    if startDay == endDay:
        res = calendar.monthrange(endDay.year, endDay.month)
        day = res[1]
        endDay = date(endDay.year, endDay.month, day)

    msg = {
        "DateStart": startDay,
        "DateEnd": endDay,
        "AccountEMP": account,
    }

    url = "https://survey.fpt.vn/api/v1/get-detail-point-emp"
    dict_tmp = []
    try:
        res = requests.post(url=url, data=msg)
        data = res.json()
        dict_tmp = data['detail']
    except Exception as ex:
        print("loi khi lay data >> {}: {} khong cho ket qua json  ".format(ex, url))
    return dict_tmp


# hien chi tiet so diem CSAT nhan vien
def count_point(detail, pointType):
    p1 = p2 = p3 = p4 = p5 = 0
    dict_cem = {"Point_5": p5, "Point_4": p4, "Point_3": p3, "Point_2": p2, "Point_1": p1}
    if detail:
        for i in detail:
            point = i[pointType]
            if point == 5:
                p5 += 1
            elif point == 4:
                p4 += 1
            elif point == 3:
                p3 += 1
            elif point == 2:
                p2 += 1
            elif point == 1:
                p1 += 1
        dict_cem['Point_5'] = p5
        dict_cem['Point_4'] = p4
        dict_cem['Point_3'] = p3
        dict_cem['Point_2'] = p2
        dict_cem['Point_1'] = p1
    totalPoint = p1 * 1 + p2 * 2 + p3 * 3 + p4 * 4 + p5 * 5
    totalSurvey = p1 + p2 + p3 + p4 + p5
    listPointInteger = [p1, p2, p3, p4, p5]
    return dict_cem, totalPoint, totalSurvey, listPointInteger


def get_csat_chart_month(**kwargs):
    typeKpi = kwargs.pop('type', None)
    dateMonth = kwargs.pop('date', None)
    account = kwargs.pop('account', None)

    result = {}
    dictMonth = {}
    dictPointMonth = {}
    listPointTK = {}
    listPointBT = {}
    listResult = []
    target = 0

    startDay = datetime(dateMonth.year, 1, 1)
    endDay = last_day_of_month(dateMonth)
    i = 1

    dict_csat = get_detail_point_emp_csat(start=startDay, end=endDay, account=account)

    # lấy thông tin target && thông tin mô tả điểm csat (infoTarget, desKpi)
    kpiCon = KpiInfo.objects.filter(kpi_type=typeKpi)
    for infoCon in kpiCon:
        target = infoCon.target
        data = json.loads(infoCon.kpi_value)
        # result['infoTarget'] = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
        #     infoCon.year) + " là " + start_tag_b_html + ">= " + str(format_number(infoCon.target)) + " điểm" + end_tag_b_html + end_tag_div_html
        # listText = infoCon.description.split(" = ")
        # result['desKpi'] = start_tag_div_html + start_tag_b_html + "•  " + listText[0] + " = " + end_tag_b_html + listText[1] + end_tag_div_html
        result['desKpi'] = ""
        result['infoTarget'] = ""

    # khởi tạo list dictionary
    while i <= endDay.month:
        dictMonth[i] = []
        dictPointMonth[i] = {}
        listPointBT[i] = []
        listPointTK[i] = []
        i += 1

    # lọc theo ngày && lọc theo loại TK - BT
    for data in dict_csat:
        month = convert_string_date(data['TimeSurvey'], DATETIME_Y_m_d).month
        dictMonth[month].append(data)
        if data['Type'] == 1:
            listPointTK[month].append(data)
        elif data['Type'] == 2:
            listPointBT[month].append(data)

    # tạo cái dict Point cho từng pointMonth
    pointMonth = 1
    while pointMonth <= endDay.month:
        dictPointMonth[pointMonth]['pointTV_tk'] = count_point(listPointTK[pointMonth], 'PointTV')
        dictPointMonth[pointMonth]['pointNet_tk'] = count_point(listPointTK[pointMonth], 'PointNet')
        # dictPointMonth[pointMonth]['point_tk'] = count_point(listPointTK[pointMonth], 'Point')
        dictPointMonth[pointMonth]['pointTV_bt'] = count_point(listPointBT[pointMonth], 'PointTV')
        dictPointMonth[pointMonth]['pointNet_bt'] = count_point(listPointBT[pointMonth], 'PointNet')
        # dictPointMonth[pointMonth]['point_bt'] = count_point(listPointBT[pointMonth], 'Point')
        dictPointMonth[pointMonth]['point_NV'] = count_point(dictMonth[pointMonth], 'Point')
        pointMonth += 1

    listResult = []
    if typeKpi == 'csat_dv':
        for key, value in dictMonth.items():
            totalPointCSAT = 0
            averagePoint = 0
            totalSurvey = 0
            isPass = True
            kpiDate = str(key) + "/" + str(dateMonth.year)
            dictTV, pointTV, countSurveyTV, listPointTV = count_point(value, 'PointTV')
            dictNet, pointNet, countSurveyNet, listPointNet = count_point(value, 'PointNet')
            totalPointCSAT += pointTV + pointNet
            if value:
                totalSurvey += countSurveyTV + countSurveyNet

                if totalSurvey != 0:
                    averagePoint = totalPointCSAT / totalSurvey
                    if averagePoint < target:
                        isPass = False

            listResult.append({
                "order": key,
                "totalPointCSAT": totalPointCSAT,
                "totalSurvey": totalSurvey,
                "averagePoint": format_number(float('{:.2f}'.format(averagePoint))),
                "isPass": isPass,
                "kpiDate": kpiDate,
                "listCsat": [
                    {
                        "title": "TK net",
                        "listPoint": dictPointMonth[key]['pointNet_tk'][3]
                    },
                    {
                        "title": "TK truyền hình",
                        "listPoint": dictPointMonth[key]['pointTV_tk'][3]
                    },
                    {
                        "title": "BT net",
                        "listPoint": dictPointMonth[key]['pointNet_bt'][3]
                    },
                    {
                        "title": "BT truyền hình",
                        "listPoint": dictPointMonth[key]['pointTV_bt'][3]
                    }
                ]
            })
    elif typeKpi == 'csat_nv':
        for key, value in dictMonth.items():
            totalPointCSAT = 0
            averagePoint = 0
            totalSurvey = 0
            isPass = True
            kpiDate = str(key) + "/" + str(dateMonth.year)
            dictTV, point, countSurvey, listPoint = count_point(value, 'Point')
            totalPointCSAT += point
            if value:
                totalSurvey += countSurvey

                if totalSurvey != 0:
                    averagePoint = totalPointCSAT / totalSurvey
                    if averagePoint < target:
                        isPass = False

            listResult.append({
                "order": key,
                "totalPointCSAT": totalPointCSAT,
                "totalSurvey": totalSurvey,
                "averagePoint": format_number(float('{:.2f}'.format(averagePoint))),
                "isPass": isPass,
                "kpiDate": kpiDate,
                "listCsat": [
                    {
                        "title": "Nhân viên",
                        "listPoint": dictPointMonth[key]['point_NV'][3]
                    },
                ]
            })

    result['listChart'] = listResult

    return result


def get_csat_chart_day(**kwargs):
    typeKpi = kwargs.pop('type', None)
    dateMonth = kwargs.pop('date', None)
    account = kwargs.pop('account', None)

    target = 0

    result = {}
    dictDay = {}
    dictPointDay = {}
    listPointTK = {}
    listPointBT = {}
    startDayOfMonth = datetime(dateMonth.year, dateMonth.month, 1)
    endDayOfMonth = dateMonth

    i = 1

    dict_csat = get_detail_point_emp_csat(start=startDayOfMonth, end=endDayOfMonth, account=account)

    # lấy thông tin target && thông tin mô tả điểm csat (infoTarget, desKpi)
    kpiCon = KpiInfo.objects.filter(kpi_type=typeKpi)
    for infoCon in kpiCon:
        target = infoCon.target
        data = json.loads(infoCon.kpi_value)
        # result['infoTarget'] = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
        #     infoCon.year) + " là " + start_tag_b_html + ">= " + str(format_number(infoCon.target)) + " điểm" + end_tag_b_html + end_tag_div_html
        # listText = infoCon.description.split(" = ")
        # result['desKpi'] = start_tag_div_html + start_tag_b_html + "•  " + listText[0] + " = " + end_tag_b_html + listText[1] + end_tag_div_html
        result['desKpi'] = ""
        result['infoTarget'] = ""

    # khởi tạo list dictionary
    while i <= endDayOfMonth.day:
        dictDay[i] = []
        dictPointDay[i] = {}
        listPointBT[i] = []
        listPointTK[i] = []
        i += 1

    # lọc theo ngày && lọc theo loại TK - BT
    if dict_csat is not None:
        for data in dict_csat:
            day = convert_string_date(data['TimeSurvey'], DATETIME_Y_m_d).day
            dictDay[day].append(data)
            if data['Type'] == 1:
                listPointTK[day].append(data)
            elif data['Type'] == 2:
                listPointBT[day].append(data)

    # tạo cái dict Point cho từng pointDay
    pointDay = 1
    while pointDay <= endDayOfMonth.day:
        dictPointDay[pointDay]['pointTV_tk'] = count_point(listPointTK[pointDay], 'PointTV')
        dictPointDay[pointDay]['pointNet_tk'] = count_point(listPointTK[pointDay], 'PointNet')
        # dictPointDay[pointDay]['point_tk'] = count_point(listPointTK[pointDay], 'Point')
        dictPointDay[pointDay]['pointTV_bt'] = count_point(listPointBT[pointDay], 'PointTV')
        dictPointDay[pointDay]['pointNet_bt'] = count_point(listPointBT[pointDay], 'PointNet')
        # dictPointDay[pointDay]['point_bt'] = count_point(listPointBT[pointDay], 'Point')
        dictPointDay[pointDay]['point_NV'] = count_point(dictDay[pointDay], 'Point')
        pointDay += 1

    listResult = []
    if typeKpi == 'csat_dv':
        for key, value in dictDay.items():
            totalPointCSAT = 0
            averagePoint = 0
            totalSurvey = 0
            isPass = True
            kpiDate = str(key) + "/" + str(startDayOfMonth.month) + "/" + str(startDayOfMonth.year)
            dictTV, pointTV, countSurveyTV, listPointTV = count_point(value, 'PointTV')
            dictNet, pointNet, countSurveyNet, listPointNet = count_point(value, 'PointNet')
            totalPointCSAT += pointTV + pointNet
            if value:
                totalSurvey += countSurveyTV + countSurveyNet

                if totalSurvey != 0:
                    averagePoint = totalPointCSAT / totalSurvey
                    if averagePoint < target:
                        isPass = False

            listResult.append({
                "order": key,
                "totalPointCSAT": totalPointCSAT,
                "totalSurvey": totalSurvey,
                "averagePoint": format_number(float('{:.2f}'.format(averagePoint))),
                "isPass": isPass,
                "kpiDate": kpiDate,
                "listCsat": [
                    {
                        "title": "TK net",
                        "listPoint": dictPointDay[key]['pointNet_tk'][3]
                    },
                    {
                        "title": "TK truyền hình",
                        "listPoint": dictPointDay[key]['pointTV_tk'][3]
                    },
                    {
                        "title": "BT net",
                        "listPoint": dictPointDay[key]['pointNet_bt'][3]
                    },
                    {
                        "title": "BT truyền hình",
                        "listPoint": dictPointDay[key]['pointTV_bt'][3]
                    }
                ]
            })
    elif typeKpi == 'csat_nv':
        for key, value in dictDay.items():
            totalPointCSAT = 0
            averagePoint = 0
            totalSurvey = 0
            isPass = True
            kpiDate = str(key) + "/" + str(startDayOfMonth.month) + "/" + str(startDayOfMonth.year)
            dictTV, point, countSurvey, listPoint = count_point(value, 'Point')
            totalPointCSAT += point
            if value:
                totalSurvey += countSurvey

                if totalSurvey != 0:
                    averagePoint = totalPointCSAT / totalSurvey
                    if averagePoint < target:
                        isPass = False

            listResult.append({
                "order": key,
                "totalPointCSAT": totalPointCSAT,
                "totalSurvey": totalSurvey,
                "averagePoint": format_number(float('{:.2f}'.format(averagePoint))),
                "isPass": isPass,
                "kpiDate": kpiDate,
                "listCsat": [
                    {
                        "title": "Nhân viên",
                        "listPoint": dictPointDay[key]['point_NV'][3]
                    }
                ]
            })

    result['listChart'] = listResult

    return result


def get_fake_data_kpi(config_key, email):
    fakeData = None
    account = None
    empCode = None
    result = {}

    redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                       , port=project_settings.REDIS_PORT_CENTRALIZED
                                       , db=project_settings.REDIS_INFO_KPI_DATABASE_CENTRALIZED,
                                       password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                       , decode_responses=True, charset="utf-8")
    data = redis_instance.get('fakeAccountInfo')
    if data:
        json_data = json.loads(data)
        if email in json_data:
            infoFake = json_data[email].split('-')
            result['empCode'] = infoFake[0]
            result['account'] = infoFake[1]
    else:
        data = JobConfigs.objects.filter(config_key=config_key).values()
        secondTimeOut = getSecondFromNowToLastOfDay()
        if data:
            for con in data:
                raw = con['config_value']
                redis_instance.set('fakeAccountInfo', raw, secondTimeOut)
                fakeData = json.loads(raw)
        if email in fakeData:
            infoFake = fakeData[email].split('-')
            result['empCode'] = infoFake[0]
            result['account'] = infoFake[1]

    return result


class KpiView(ViewSet):
    def get_kpi_result(self, request):
        """
        kpi_ontime: Đúng hẹn (TK + BT)
        kpi_sla: Tỷ lệ triển khai bảo trì được tích hẹn và hoàn tất trong ngày
        kpi_2cl: Số Checklist lặp (>=2/30 ngày)
        kpi_3cl: Số Checklist lặp (>3/30 ngày)
        kpi_csat_cldv: CSAT Chất lượng dịch vụ
        kpi_csat_nvkt: CSAT Nhân viên kỹ thuật
        kpi_clps_7n: Tổng số lượng checklist 7 ngày (TK + BT)
        """
        try:
            data_input = request.GET.copy()
            startDay = request.GET['startDay']
            endDay = request.GET['endDay']
            lastMonth = request.GET['lastMonth']
            account = "null"
            empCode = ""
            pointData = []
            dictCsat = {}

            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))

            # kiểm tra thông tin nv lấy data giả
            fakeAccount = get_fake_data_kpi('KPI_EMPLOYEES_FAKE_INFO', data_token['email'])
            if fakeAccount:
                account = fakeAccount['account']
                empCode = fakeAccount['empCode']
            else:
                mydata = KpiTask.objects.filter(emp_code=data_token['empCode']).values().last()
                if mydata:
                    account = mydata['account_mbn']
                    empCode = mydata['emp_code']

            # Kiểm tra input TH startDay, endDay, lastMonth đều có value hoặc đều null
            if startDay and endDay and lastMonth:
                api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="get_kpi_result", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT)
                return response_data(status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT)
            elif not startDay and not endDay and not lastMonth:
                api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="get_kpi_result", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_NO_INPUT)
                return response_data(status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_NO_INPUT)

            # Kiểm tra lấy biến lastMonth or startDay, endDay
            if startDay and endDay:
                if check_valid_date(startDay, day_month_YEAR) is False or check_valid_date(endDay,
                                                                                           day_month_YEAR) is False:
                    api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="get_kpi_result", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_FORMAT)
                    return response_data(status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_FORMAT)
                to = convert_string_date(startDay, day_month_YEAR)
                end = convert_string_date(endDay, day_month_YEAR)
                pointData = KpiTask.objects.filter(kpi_date__range=[to, end], emp_code=empCode)
                dictCsat = get_csat_average_result(start=to, end=end, account=account)
            elif lastMonth:
                if check_valid_date(lastMonth, month_YEAR) is False:
                    api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=-1, api_name="get_kpi_result", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_FORMAT)
                    return response_data(status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_FORMAT)
                dateFormate = convert_string_date(lastMonth, month_YEAR)
                pointData = KpiTask.objects.filter(kpi_date__month=dateFormate.month, kpi_date__year=dateFormate.year,
                                                   emp_code=empCode)
                dictCsat = get_csat_average_result(start=dateFormate, end=dateFormate, account=account)

            kpiList = ['kpi_ontime', 'kpi_sla', 'kh2cl', 'kh3cl', 'clps_7n']
            csatList = ['csat_dv', 'csat_nv']
            listKPI = []
            result = {}
            total_tk_bt = 0
            count_ontime_tk_bt = 0
            total_sla = 0
            count_sla = 0
            total_2cl = 0
            total_3cl = 0
            count_clps7n = 0
            total_customer_cl = 0

            desDV = ""
            desNV = ""

            kpiCon = KpiInfo.objects.all()
            # nếu data rỗng trả về 0 của những chỉ số kpi
            if not pointData:
                for configKpi in kpiCon:
                    if configKpi.kpi_type in kpiList:
                        data = json.loads(configKpi.kpi_value)
                        kpiType = configKpi.kpi_type
                        kpiTitle = configKpi.title
                        isPass = True
                        kpi = {
                            "type": kpiType,
                            "percent": 0,
                            "title": kpiTitle,
                            "desTitle": data['subTitle'],
                            "isPass": isPass
                        }
                        listKPI.append(kpi)
            else:
                for x in pointData:
                    # tổng số ca đúng hẹn - trễ hẹn (TK + BT)
                    total_tk_bt += x.ontime_tk + x.late_tk + x.ontime_bt + x.late_bt
                    count_ontime_tk_bt += x.ontime_tk + x.ontime_bt
                    # tổng số ca sla (TK + BT)
                    total_sla += x.count_shift_sla_tk + x.count_shift_sla_bt
                    count_sla += x.count_shift_complete_sla_tk + x.count_shift_complete_sla_bt
                    # tổng số ca checklist2 - checklist3
                    total_2cl += x.count_cl2
                    total_3cl += x.count_cl3
                    # tổng sl KH có check
                    total_customer_cl += x.customer_cl
                    count_clps7n += x.count_cl7n_bt + x.count_cl7n_tk

                for configKpi in kpiCon:
                    if configKpi.kpi_type in kpiList:
                        data = json.loads(configKpi.kpi_value)
                        kpiType = configKpi.kpi_type
                        kpiTitle = configKpi.title
                        target = configKpi.target
                        isPass = True
                        overPass = 100
                        kpi = {
                            "type": kpiType,
                            "percent": 0,
                            "title": kpiTitle,
                            "desTitle": data['subTitle'],
                            "isPass": isPass
                        }

                        if kpi['type'] == 'kpi_ontime':
                            if total_tk_bt != 0:
                                percent = float('{:.2f}'.format((count_ontime_tk_bt / total_tk_bt) * 100))
                                kpi['percent'] = format_number(percent)
                                if percent < target:
                                    kpi['isPass'] = False

                        if kpi['type'] == 'kpi_sla':
                            if total_sla != 0:
                                percent = float('{:.2f}'.format((count_sla / total_sla) * 100))
                                kpi['percent'] = format_number(percent)
                                if percent < target:
                                    kpi['isPass'] = False

                        if kpi['type'] == 'kh2cl':
                            if total_customer_cl != 0:
                                percent = float('{:.2f}'.format((total_2cl / total_customer_cl) * 100))
                                kpi['percent'] = format_number(percent)
                                if percent > target:
                                    kpi['isPass'] = False

                        if kpi['type'] == 'kh3cl':
                            if total_customer_cl != 0:
                                percent = float('{:.2f}'.format((total_3cl / total_customer_cl) * 100))
                                kpi['percent'] = format_number(percent)
                                if percent > target:
                                    kpi['isPass'] = False

                        if kpi['type'] == 'clps_7n':
                            if total_tk_bt != 0:
                                percent = float('{:.2f}'.format((count_clps7n / total_tk_bt) * 100))
                                kpi['percent'] = format_number(percent)
                                if percent > target:
                                    kpi['isPass'] = False

                        listKPI.append(kpi)

            for configKpi in kpiCon:
                if configKpi.kpi_type in csatList:
                    data = json.loads(configKpi.kpi_value)
                    cut_string = configKpi.kpi_type.split("_")
                    csatType = "point" + cut_string[0].title() + cut_string[-1].upper()
                    csatTitle = configKpi.title
                    isPass = True
                    overPass = 5
                    result[csatType] = {
                        "percent": 0,
                        "isPass": isPass,
                        "title": csatTitle,
                        "desTitle": data['subTitle'],
                        "type": configKpi.kpi_type
                    }

                    # lấy thông tin subTitle và description
                    if result[csatType]['type'] == 'csat_dv':
                        result[csatType]['percent'] = dictCsat['csat_dv']
                        desDV = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
                            configKpi.year) + " là " + start_tag_b_html + ">= " + str(
                            configKpi.target) + " điểm" + end_tag_b_html + end_tag_div_html
                        if result[csatType]['percent'] < configKpi.target:
                            result[csatType]['isPass'] = False
                        if result[csatType]['percent'] > overPass:
                            result[csatType]['percent'] = overPass

                    if result[csatType]['type'] == 'csat_nv':
                        result[csatType]['percent'] = dictCsat['csat_nv']
                        desNV = start_tag_div_html + start_tag_b_html + "•  " + data['info'] + end_tag_b_html + " trong KPIs năm " + str(
                            configKpi.year) + " là " + start_tag_b_html + ">= " + str(
                            configKpi.target) + " điểm" + end_tag_b_html + end_tag_div_html
                        if result[csatType]['percent'] < configKpi.target:
                            result[csatType]['isPass'] = False
                        if result[csatType]['percent'] > overPass:
                            result[csatType]['percent'] = overPass

            result['listKPI'] = listKPI
            # hai biến nào để rỗng vì do yêu cầu từ phía bộ phận PTQ
            result['csatStaff'] = ""
            result['csatService'] = ""

            # check dữ liệu rỗng thì trả statusCode = 6
            if result is None or not result:
                api_save_log(request=request, data_input=data_input, api_name="get_kpi_result", status_code=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA)
                return response_data(status=STATUS_CODE_NO_DATA, data=None, message=MESSAGE_API_NO_DATA)
            api_save_log(request=request, data_input=data_input, data_output=result, api_name="get_kpi_result")
            return response_data(data=result)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_kpi_result.__name__, ex))
            api_save_log(request=request, data_input=data_input, api_status=0, err_analysis=0, api_name="get_kpi_result", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def get_kpi_list_chart(self, request):
        try:
            getData = request.GET
            kpiType = getData['type']
            kpiDate = getData['date']
            kpiMonth = getData['month']
            account = "null"
            empCode = ""
            result = {}
            action_type = None
            try:
                if kpiType.lower() == "kpi_ontime":
                    action_type = 0
                elif kpiType.lower() == "kpi_sla":
                    action_type = 1
                elif kpiType.lower() == "kh2cl":
                    action_type = 2
                elif kpiType.lower() == "kh3cl":
                    action_type = 3
                elif kpiType.lower() == "clps_7n":
                    action_type = 4
            except:
                pass

            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))

            # kiểm tra thông tin nv lấy data giả
            fakeAccount = get_fake_data_kpi('KPI_EMPLOYEES_FAKE_INFO', data_token['email'])
            if fakeAccount:
                empCode = fakeAccount['empCode']
            else:
                mydata = KpiTask.objects.filter(emp_code=data_token['empCode']).values().last()
                if mydata:
                    # account = mydata['account_mbn']
                    empCode = mydata['emp_code']

            if kpiType:
                # check quy định input
                if kpiMonth and kpiDate:
                    api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_kpi_list_chart", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                    return response_data(message=MESSAGE_API_INVALID_INPUT, status=STATUS_CODE_INVALID_INPUT)

                # check định dạng input và xét đúng tác vu thuc hien
                if kpiMonth and check_valid_date(kpiMonth, month_YEAR):
                    result = get_kpi_month(type=kpiType, date=kpiMonth, emp_code=empCode)
                elif kpiDate and check_valid_date(kpiDate, day_month_YEAR):
                    result = get_kpi_day(type=kpiType, date=kpiDate, emp_code=empCode)
                else:
                    api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_kpi_list_chart", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                    return response_data(message=MESSAGE_API_INVALID_INPUT, status=STATUS_CODE_INVALID_INPUT)
            else:
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_kpi_list_chart", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_NO_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                return response_data(message=MESSAGE_API_NO_INPUT, status=STATUS_CODE_INVALID_INPUT)

            # check dữ liệu rỗng thì trả statusCode = 6
            if result is None or not result:
                api_save_log(request=request, data_input=getData, api_name="get_kpi_list_chart", status_code=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                return response_data(status=STATUS_CODE_NO_DATA, data=None, message=MESSAGE_API_NO_DATA)
            api_save_log(request=request, data_input=getData, data_output=result, api_name="get_kpi_list_chart", jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
            return response_data(data=result)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_kpi_list_chart.__name__, ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="get_kpi_list_chart", status_code=STATUS_CODE_FAILED, message=str(ex), jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def get_kpi_detail_info(self, request):
        try:
            getData = request.GET
            kpiType = getData['type']
            kpiDate = getData['date']
            kpiMonth = getData['month']
            account = "null"
            empCode = ""
            action_type = None
            try:
                if kpiType.lower() == "kpi_ontime":
                    action_type = 0
                elif kpiType.lower() == "kpi_sla":
                    action_type = 1
                elif kpiType.lower() == "kh2cl":
                    action_type = 2
                elif kpiType.lower() == "kh3cl":
                    action_type = 3
                elif kpiType.lower() == "clps_7n":
                    action_type = 4
            except:
                pass

            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))

            # kiểm tra thông tin nv lấy data giả
            fakeAccount = get_fake_data_kpi('KPI_EMPLOYEES_FAKE_INFO', data_token['email'])
            if fakeAccount:
                empCode = fakeAccount['empCode']
            else:
                mydata = KpiTask.objects.filter(emp_code=data_token['empCode']).values().last()
                if mydata:
                    # account = mydata['account_mbn']
                    empCode = mydata['emp_code']

            if kpiType and kpiType in ['kpi_sla', 'kpi_ontime', 'kh2cl', 'kh3cl', 'clps_7n']:
                # check quy định input
                if kpiMonth and kpiDate:
                    api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_kpi_detail_info", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                    return response_data(message=MESSAGE_API_INVALID_INPUT, status=STATUS_CODE_INVALID_INPUT)

                # check định dạng input và xét đúng tác vu thuc hien
                if kpiMonth and check_valid_date(kpiMonth, month_YEAR):
                    result = get_kpi_month_info(type=kpiType, date=kpiMonth, emp_code=empCode)
                elif kpiDate and check_valid_date(kpiDate, day_month_YEAR):
                    result = get_kpi_day_info(type=kpiType, date=kpiDate, emp_code=empCode)
                else:
                    api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_kpi_detail_info", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                    return response_data(message=MESSAGE_API_INVALID_INPUT, status=STATUS_CODE_INVALID_INPUT)
            else:
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_kpi_detail_info", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_NO_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                return response_data(message=MESSAGE_API_NO_INPUT, status=STATUS_CODE_INVALID_INPUT)

            # check dữ liệu rỗng thì trả statusCode = 6
            if result['listContract'] is None or not result['listContract']:
                api_save_log(request=request, data_input=getData, api_name="get_kpi_detail_info", status_code=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                return response_data(status=STATUS_CODE_NO_DATA, data=None, message=MESSAGE_API_NO_DATA)
            api_save_log(request=request, data_input=getData, data_output=result, api_name="get_kpi_detail_info", jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
            return response_data(data=result)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_kpi_detail_info.__name__, ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="get_kpi_detail_info", status_code=STATUS_CODE_FAILED, message=str(ex), jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def get_csat_list_chart(self, request):
        try:
            getData = request.GET
            kpiType = getData['type']
            kpiDate = getData['date']
            kpiMonth = getData['month']
            account = "null"
            dictCsat = {}
            action_type = None
            try:
                if kpiType.lower() == "csat_dv":
                    action_type = 0
                elif kpiType.lower() == "csat_nv":
                    action_type = 1
            except:
                pass

            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))

            # kiểm tra thông tin nv lấy data giả
            fakeAccount = get_fake_data_kpi('KPI_EMPLOYEES_FAKE_INFO', data_token['email'])
            if fakeAccount:
                account = fakeAccount['account']
            else:
                mydata = KpiTask.objects.filter(emp_code=data_token['empCode']).values().last()
                if mydata:
                    account = mydata['account_mbn']

            if kpiType:
                # check quy định input
                if kpiMonth and kpiDate:
                    api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_csat_list_chart", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                    return response_data(message=MESSAGE_API_INVALID_INPUT, status=STATUS_CODE_INVALID_INPUT)

                # check định dạng input và xét đúng tác vu thuc hien
                if kpiMonth and check_valid_date(kpiMonth, month_YEAR):
                    convertDate = convert_string_date(kpiMonth, month_YEAR)
                    dictCsat = get_csat_chart_month(type=kpiType, date=convertDate, account=account)
                elif kpiDate and check_valid_date(kpiDate, day_month_YEAR):
                    convertDate = convert_string_date(kpiDate, day_month_YEAR)
                    dictCsat = get_csat_chart_day(type=kpiType, date=convertDate, account=account)
                else:
                    api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_csat_list_chart", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_INVALID_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                    return response_data(message=MESSAGE_API_INVALID_INPUT, status=STATUS_CODE_INVALID_INPUT)

            else:
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="get_csat_list_chart", status_code=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_NO_INPUT, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                return response_data(message=MESSAGE_API_NO_INPUT, status=STATUS_CODE_INVALID_INPUT)
            # check dữ liệu rỗng thì trả statusCode = 6
            if dictCsat is None or not dictCsat:
                api_save_log(request=request, data_input=getData, api_name="get_csat_list_chart", status_code=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA, jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
                return response_data(status=STATUS_CODE_NO_DATA, data=None, message=MESSAGE_API_NO_DATA)
            api_save_log(request=request, data_input=getData, data_output=dictCsat, api_name="get_csat_list_chart", jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
            return response_data(data=dictCsat)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_csat_list_chart.__name__, ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="get_csat_list_chart", status_code=STATUS_CODE_FAILED, message=str(ex), jsonParamsRequired=f'type={kpiType.lower()}', action_type=action_type)
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def view_all(self, request):
        queryset = JobConfigs.objects.all()
        serializer = JobConfigsSerializer(queryset, many=True)
        return Response(serializer.data)
