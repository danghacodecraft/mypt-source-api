from rest_framework import serializers

from ...http.apis.inside_api import *
from ...core.entities.redis_service import RedisService
from ...core.helpers import my_datetime
from ...core.helpers.global_variable import *
from ...core.helpers.utils import *
from ...http.models.salary_daily_total import SalaryDailyTotal
from ...http.models.salary_monthly import SalaryMonthly
from ...http.models.salary_daily import SalaryDaily
from ...http.serializers.salary_configs_serializer import SalaryConfigsSerializer
from ...http.apis.profile_api import (
    get_all_employee_empty_salary_daily,
    get_all_employee_empty_salary_monthly,
    update_employee_salary_day_sync_status,
    update_employee_salary_month_sync_status
)


class SalaryDailySerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source='employee_code')
    cache = {}

    class Meta:
        model = SalaryDaily
        fields = ['employee_code']

    class SalaryMonthly:
        model = SalaryMonthly
        fields = ['employee_code']

    def __init__(self):
        redis_service = RedisService()
        self.cache = redis_service.redis_service

    def getSalaryOfEmployeeByDate(self, _employee_code, _year, _month, _day, _employee_email):
        salaryCacheKey = '{}:{}:{}:{}:{}'.format(SALARY_DAILY_CACHE_KEY_NAME, _year, _month, _day, _employee_code)
        dataCache = self.cache.get(salaryCacheKey)
        if not empty(dataCache):
            salaryInfo = json.loads(dataCache)
            return {
                'salary_total': salaryInfo.get('salary_total', 0),
                'salary_details': salaryInfo.get('salary_details', [])
            }

        dailyStruct = SalaryConfigsSerializer.getContentByKey('SALARY_DAILY_STRUCT')
        # Xử lý cấu trúc response details khi total=0
        emptyDetails = []
        if not empty(dailyStruct):
            emptyDetails = getSalaryEmptyObj(_item=dailyStruct)
            emptyDetails = emptyDetails.get('details', [])

        responseDefault = {
            'salary_total': 0,
            'salary_details': emptyDetails
        }

        if _day < 1:
            # ngay hien tai - 1
            dateTo = my_datetime.getDate(-1)
            # ngay 1 của ngày hiện tại - 1
            dateFrom = my_datetime.createDatetime(dateTo.year, dateTo.month, 1)
            data = SalaryDailyTotal.objects.filter(employee_code=_employee_code, year_calculate=dateTo.year,
                                                   month_calculate=dateTo.month,
                                                   day_last_calculate=dateTo.day).values(
                'salary_total', 'salary_details', 'salary_inside_details')
            data = list(data)
            if len(data) < 1:
                insideData = self.syncInsideDataDailyTotal(_employee_code, _employee_email, dateFrom, dateTo)
                if empty(insideData) or (insideData.get('status', False) == False) \
                        or empty(insideData.get('inside_data', None)):
                    return responseDefault
                insideDetails = insideData.get('inside_data', [])
                salaryTotal = insideData.get('total', 0)

                if type(salaryTotal) != int:
                    salaryTotal = int(salaryTotal)
                if empty(dailyStruct):
                    salaryDetail = []
                else:
                    salaryDetail = getSalaryObj(_item=dailyStruct, _value_list=insideDetails)
                res = {
                    'salary_total': salaryTotal,
                    'salary_details': salaryDetail.get('details', []),
                    'salary_inside_details': insideDetails
                }
            else:
                res = data[0]

        else:
            data = SalaryDaily.objects.filter(employee_code=_employee_code, year_calculate=_year,
                                              month_calculate=_month, day_calculate=_day).values('salary_total',
                                                                                                 'salary_details',
                                                                                                 'salary_inside_details')
            data = list(data)
            if len(data) == 0:
                insideData = self.syncInsideData(_employee_code, _employee_email, _year, _month, _day)

                if empty(insideData) or (insideData.get('status', False) == False) \
                        or empty(insideData.get('inside_data', None)):
                    return responseDefault
                insideDetails = insideData.get('inside_data', [])
                salaryTotal = insideData.get('total', 0)
                if type(salaryTotal) != int:
                    salaryTotal = int(salaryTotal)
                if empty(dailyStruct):
                    salaryDetail = []
                else:
                    salaryDetail = getSalaryObj(_item=dailyStruct, _value_list=insideDetails)
                res = {
                    'salary_total': salaryTotal,
                    'salary_details': salaryDetail.get('details', []),
                    'salary_inside_details': insideDetails
                }
            else:
                res = data[0]

        if empty(res['salary_details']):
            if empty(res['salary_inside_details']):
                res['salary_details'] = emptyDetails
            else:
                if empty(dailyStruct):
                    res['salary_details'] = emptyDetails
                else:
                    salaryDetail = getSalaryObj(_item=dailyStruct, _value_list=res['salary_inside_details'])
                    res['salary_details'] = salaryDetail.get('details', emptyDetails)

        # xử lý lưu cache
        cacheSalaryTimeOut = SALARY_CACHE_DEFAULT_TIMEOUT
        if not empty(res['salary_details']) or _day < my_datetime.getDate(-1).day:
            # Nếu có thông tin lương thì cache hoặc nếu không có thông tin lương nhưng thời gian get là trong quá khứ
            # (2 ngày trước) thì vẫn lưu. vì lương chỉ trễ 1 ngày, không có là không có luôn rồi không cần tìm nữa
            cacheSalaryTimeOut = my_datetime.getSecondFromNowToLastOfDay()  # Tính đến ngày này của tháng sau
        res = {
            'salary_total': res.get('salary_total', 0),
            'salary_details': res.get('salary_details', emptyDetails)
        }
        if _day > 0:
            self.cache.set(salaryCacheKey,
                           json.dumps(res),
                           cacheSalaryTimeOut)
        return res

    def formatSalaryInsideData(self, _data):
        newJson = {}
        for value in _data:
            id = value.get('id', '')
            if (not empty(id)):
                newJson[id] = value
        return newJson

    def getAllDaySalaryOfEmployee(self, _employee_code, _year, _month, _day, _employee_email):
        total = 0
        header = {
            "date": "Ngày",
            "total": "Tổng",
            "BasicSalary": "Lương\nbậc nghề",
            "SumProductivitySalary": "Lương \nsản phẩm",
            # thêm khoản trắng để check server trả về là giá trị mặc định hay config
            "SumQuantitySalary": "Lương\nCLDV"
        }
        salaryCacheKey = '{}:{}:{}:{}'.format(SALARY_DAILY_OVERVIEW_CACHE_KEY_NAME, _year, _month, _employee_code)
        dataCache = self.cache.get(salaryCacheKey)
        if not empty(dataCache):
            salaryInfo = json.loads(dataCache)
            # header = salaryInfo.get('salary_details', [])
            return {
                'salary_total': salaryInfo.get('salary_total', 0),
                'salary_details': salaryInfo.get('salary_details', []),
                'salary_header': salaryInfo.get('salary_header', header)
            }
        dataList = []
        responseDefault = {
            'salary_total': 0,
            'salary_details': [],
            'salary_header': header
        }
        # lay tat ca luong ngay cua thang _month
        data = SalaryDaily.objects.filter(employee_code=_employee_code, year_calculate=_year,
                                          month_calculate=_month) \
            .order_by('-day_calculate') \
            .values('salary_total',
                    'salary_inside_details',
                    'day_calculate',
                    'employee_code',
                    'month_calculate',
                    'year_calculate') \
            .distinct()
        print(data.query)
        dailyStruct = SalaryConfigsSerializer.getContentByKey('SALARY_DAILY_OVERVIEW_ITEM_STRUCT')
        if empty(dailyStruct):
            return responseDefault
        prevDay = _day
        hasCache = False
        last_day = -1
        if len(data) > 0:
            # chạy vòng lặp qua từng ngày
            for value in data:
                spaceDay = value['day_calculate']
                if last_day < 0:
                    if spaceDay == _day:
                        hasCache = True
                    else:
                        # Không có dữ liệu ngày hiện tại
                        hasCache = False
                    last_day = value['day_calculate']

                # Điền giá trị 0 cho nhung ngay khong co data luong
                while (prevDay - spaceDay) > 0:
                    row = {}
                    dateStr = '{:02d}/{}/{}'.format(prevDay, _month, _year)
                    for i in dailyStruct:
                        key = i.get('myptId', '')
                        if empty(key):
                            continue
                        spaceValue = '0'
                        if key == 'date':
                            spaceValue = dateStr
                        header[key] = i.get('myptName', '')
                        row[key] = spaceValue
                    dataList.append(row)
                    prevDay -= 1

                # lay luong khi có data
                dateStr = '{:02d}/{}/{}'.format(value['day_calculate'], _month, _year)
                insideData = value['salary_inside_details']
                total += value['salary_total']
                if empty(insideData):
                    continue
                row = {}
                for i in dailyStruct:
                    key = i.get('myptId', '')
                    if empty(key):
                        continue
                    insideId = i.get('insideId', '')
                    b_value = ''
                    if empty(insideId):
                        if key == 'date':
                            b_value = dateStr
                    else:
                        b_value = insideData[insideId].get('value', 0)
                    header[key] = i.get('myptName', '')
                    row[key] = numberFormat(b_value)
                prevDay = value['day_calculate'] - 1
                dataList.append(row)

        # update ngày 0 (khi lương các ngày đầu tháng không có, nên phải set = 0)
        while prevDay > 0:
            # Điền giá trị 0
            row = {}
            dateStr = '{:02d}/{}/{}'.format(prevDay, _month, _year)
            for i in dailyStruct:
                key = i.get('myptId', '')
                if empty(key):
                    continue
                spaceValue = '0'
                if key == 'date':
                    spaceValue = dateStr
                header[key] = i.get('myptName', '')
                row[key] = spaceValue
            dataList.append(row)
            prevDay -= 1
        res = {
            'salary_total': total,
            'salary_details': dataList,
            'salary_header': header
        }

        # xử lý lưu cache
        cacheSalaryTimeOut = SALARY_CACHE_DEFAULT_TIMEOUT
        if hasCache:
            cacheSalaryTimeOut = my_datetime.getSecondFromNowToLastOfDay()  # Tính đến cuối ngày
        self.cache.set(salaryCacheKey,
                       json.dumps(res),
                       cacheSalaryTimeOut)
        return res

    def getHomeInfo(self, _employee_code, _year, _month):
        salaryTotal = 0
        salaryDetails = []
        dailyStruct = SalaryConfigsSerializer.getContentByKey('SALARY_DAILY_HOME_STRUCT')
        if not empty(dailyStruct):
            data = SalaryDailyTotal.objects.filter(employee_code=_employee_code, year_calculate=_year,
                                                   month_calculate=_month).values('salary_total',
                                                                                  'salary_inside_details').first()
            if (empty(data)):
                items = dailyStruct.get('details', [])
                for item in items:
                    id = item['info'].get('myptId', '')
                    if empty(id):
                        continue
                    salaryDetails.append({
                        "id": id,
                        "title": item['info'].get('myptName', ''),
                        "number": "0",
                        "info": "",
                        "details": []
                    })
            else:
                salaryTotal = data.get('salary_total', 0)
                dataTotal = data.get('salary_inside_details', [])
                if empty(dataTotal):
                    # Nếu tìm không thấy dữ liệu thì cộng dồn database. Hạn chế gọi inside do timeout có thể lớn,
                    # ảnh hưởng tốc độ load ở home
                    data = SalaryDaily.objects.filter(employee_code=_employee_code, year_calculate=_year,
                                                      month_calculate=_month) \
                        .values('salary_total',
                                'salary_inside_details',
                                'day_calculate',
                                'employee_code',
                                'month_calculate',
                                'year_calculate') \
                        .distinct()
                    dataTotal = self.sumInsideData(data)
                    salaryTotal = dataTotal['SumSalaryMonth'].get('value', 0)
                salaryDetails = getSalaryObj(_item=dailyStruct, _value_list=dataTotal)
                if not empty(salaryDetails):
                    salaryDetails = salaryDetails.get('details', [])
        return {
            "salary_total": salaryTotal,
            "salary_details": salaryDetails
        }

    def sumInsideData(self, _datas):
        response = {}
        for row in _datas:
            insideData = row['salary_inside_details']
            if empty(insideData):
                continue
            for key, item in insideData.items():
                if empty(response.get(key, '')):
                    response[key] = {
                        "id": "",
                        "name": "",
                        "value": 0
                    }
                response[key]['id'] = item['id']
                response[key]['name'] = item['name']
                response[key]['value'] += item['value']
        return response

    def getSalaryOfEmployeeByMonth(self, _employee_code, _year, _month, _employee_email):
        salaryCacheKey = '{}:{}:{}:{}'.format(SALARY_MONTHLY_CACHE_KEY_NAME, _year, _month, _employee_code)
        dataCache = self.cache.get(salaryCacheKey)
        if not empty(dataCache):
            salaryInfo = json.loads(dataCache)
            return {
                'salary_total': salaryInfo.get('salary_total', 0),
                'salary_details': salaryInfo.get('salary_details', [])
            }
        dailyStruct = SalaryConfigsSerializer.getContentByKey('SALARY_MONTHLY_STRUCT_NEW')

        # Xử lý cấu trúc response details khi total=0
        emptyDetails = []
        if not empty(dailyStruct):
            emptyDetails = getSalaryEmptyObj(_item=dailyStruct)
            emptyDetails = emptyDetails.get('details', [])

        responseDefault = {
            'salary_total': 0,
            'salary_details': emptyDetails
        }
        # data = SalaryMonthly.objects.filter(employee_code=_employee_code, year_calculate=_year,
        # month_calculate=_month).values('salary_total','salary_details','salary_inside_details') data = list(data)
        # if(len(data)<1):
        insideData = self.syncInsideMonthlyData(_employee_code, _year, _month, _employee_email)
        if (empty(insideData) or (insideData.get('status', False) == False) or empty(
                insideData.get('inside_data', None))):
            return responseDefault
        insideDetails = insideData.get('inside_data', [])
        salaryTotal = insideData.get('total', 0)
        # insideDetails = []
        # salaryTotal = 0
        if type(salaryTotal) != int:
            salaryTotal = int(salaryTotal)
        salaryDetail = []
        if not empty(dailyStruct):
            salaryDetail = getSalaryObj(_item=dailyStruct, _value_list=insideDetails)
        res = {
            'salary_total': salaryTotal,
            'salary_details': salaryDetail.get('details', emptyDetails)
        }
        # xử lý lưu cache
        try:
            cacheSalaryTimeOut = SALARY_CACHE_DEFAULT_TIMEOUT
            curentDate = my_datetime.today()
            configs = SalaryConfigsSerializer.getContentByKey('SALARY_CONFIGS')
            salaryEndDayUpdate = configs.get('salary_day_stop_update', SALARY_END_DAY_IMPORT_MONTHLY)
            if not empty(res['salary_details']) and curentDate.day > salaryEndDayUpdate:
                # Nếu có thông tin lương thì và thời gian hiện tại trễ hơn thời gian nhân sự update lần cuối thì lưu
                # cache
                cacheSalaryTimeOut = my_datetime.getDateOfNextYear(my_datetime.today(),
                                                                   year=2).seconds  # Tính đến ngày này đến 2 năm sau
            self.cache.set(salaryCacheKey,
                           json.dumps(res),
                           cacheSalaryTimeOut)
        except Exception as ex:
            print('[ERROR] getSalaryOfEmployeeByMonth Salary cache error {}'.format(ex))
        return res

    def syncInsideMonthlyData(self, _employee_code, _year, _month, _employee_email):
        responseDefault = {
            'status': False,
            'inside_data': [],
            'total': 0
        }
        curentDate = my_datetime.today()
        newRow = SalaryMonthly.objects.filter(employee_code=_employee_code, year_calculate=_year,
                                              month_calculate=_month).first()
        configs = SalaryConfigsSerializer.getContentByKey('SALARY_CONFIGS')
        salaryEndDayUpdate = configs.get('salary_day_stop_update', SALARY_END_DAY_IMPORT_MONTHLY)

        if empty(newRow) or (not empty(newRow)
                             and newRow.date_row_created.year == curentDate.year
                             and newRow.date_row_created.month == curentDate.month
                             and curentDate.day < salaryEndDayUpdate):

            # Nếu đã tồn tại thì kiểm tra thêm thời gian đồng bộ, nếu thời gian đồng bộ trước ngày 15 thì xử lý ghi đè
            insideApi = InsideApi()
            month = '{}-{}'.format(_year, _month)
            data = insideApi.salary_month(_employee_code, month)
            if not data.get('status', False):
                return responseDefault
            insideData = data.get('data', [])
            if empty(insideData):
                return responseDefault
            insideDetails = self.formatSalaryInsideData(_data=insideData)
            salaryTotal = insideDetails['SumSalaryMonth'].get('value', 0)
            if type(salaryTotal) != int:
                salaryTotal = int(salaryTotal)
            if empty(newRow):
                newRow = SalaryMonthly(
                    employee_code=_employee_code,
                    employee_email=_employee_email
                )
            try:
                newRow.salary_total = salaryTotal
                newRow.salary_inside_details = insideDetails
                newRow.year_calculate = _year
                newRow.month_calculate = _month
                newRow.save()
            except Exception as ex:
                print('[ERROR] syncInsideMonthlyData Salary save error {}'.format(ex))
        else:
            salaryTotal = newRow.salary_total
            insideDetails = newRow.salary_inside_details
        return {
            'status': True,
            'inside_data': insideDetails,
            'total': salaryTotal
        }

    def syncInsideData(self, _employee_code, _employee_email, _year, _month, _day):
        responseDefault = {
            'status': False,
            'inside_data': [],
            'total': 0
        }
        insideApi = InsideApi()
        fromDate = toDate = '{}-{}-{}'.format(_year, _month, _day)
        data = insideApi.salary_provisional(_employee_code, fromDate, toDate)
        # return data
        if not data.get('status', False):
            return responseDefault
        insideData = data.get('data', [])
        if empty(insideData):
            return responseDefault
        insideDetails = self.formatSalaryInsideData(_data=insideData)
        salaryTotal = insideDetails['SumSalaryMonth'].get('value', 0)
        if type(salaryTotal) != int:
            salaryTotal = int(salaryTotal)
        # newRow = SalaryDaily(
        #     employee_code=_employee_code,
        #     employee_email=_employee_email,
        #     salary_total=salaryTotal,
        #     salary_details=None,
        #     salary_inside_details=insideDetails,
        #     year_calculate=_year,
        #     month_calculate=_month,
        #     day_calculate=_day
        # )
        try:
            # newRow.save()
            print(">> create row SalaryDaily")
            SalaryDaily.objects.update_or_create(
                employee_code=_employee_code,
                year_calculate=_year,
                month_calculate=_month,
                day_calculate=_day,
                defaults={
                    "employee_email": _employee_email,
                    "salary_total": salaryTotal,
                    "salary_details": None,
                    "salary_inside_details": insideDetails
                }
            )
        except Exception as ex:
            print('[ERROR] Salary save error {}'.format(ex))
        return {
            'status': True,
            'inside_data': insideDetails,
            'total': salaryTotal
        }

    def syncInsideDataDailyTotal(self, _employee_code, _employee_email, _from, _to):
        responseDefault = {
            'status': False,
            'inside_data': [],
            'total': 0
        }
        insideApi = InsideApi()
        fromDate = '{}-{}-{}'.format(_from.year, _from.month, _from.day)
        toDate = '{}-{}-{}'.format(_to.year, _to.month, _to.day)
        data = insideApi.salary_provisional(_employee_code, fromDate, toDate)
        # return data
        if not data.get('status', False):
            return responseDefault
        insideData = data.get('data', [])
        if empty(insideData):
            return responseDefault
        insideDetails = self.formatSalaryInsideData(_data=insideData)
        salaryTotal = insideDetails['SumSalaryMonth'].get('value', 0)
        if type(salaryTotal) != int:
            salaryTotal = int(salaryTotal)
        newRow = SalaryDailyTotal.objects.filter(employee_code=_employee_code, year_calculate=_to.year,
                                                 month_calculate=_to.month).first()
        if empty(newRow):
            newRow = SalaryDailyTotal(
                employee_code=_employee_code,
                employee_email=_employee_email
            )
        try:
            newRow.salary_total = salaryTotal
            newRow.salary_inside_details = insideDetails
            newRow.year_calculate = _to.year
            newRow.month_calculate = _to.month
            newRow.day_last_calculate = _to.day
            newRow.save()
        except Exception as ex:
            print('[ERROR] syncInsideDataDailyTotal Salary save error {}'.format(ex))
        return {
            'status': True,
            'inside_data': insideDetails,
            'total': salaryTotal
        }

    def getAllEmployeeEmptySalaryDaily(self):
        prevDate = my_datetime.getDate(-1)
        firstTimeOfDate = my_datetime.createDatetime(prevDate.year, prevDate.month, prevDate.day)
        firstTimeOfDateStr = my_datetime.dateTimeToStr(firstTimeOfDate, '%Y-%m-%d')
        data = get_all_employee_empty_salary_daily(firstTimeOfDateStr)
        return data

    def getAllEmployeeEmptySalaryMonthly(self):
        importLastDay = my_datetime.getDate(-SALARY_DAY_IMPORT_MONTHLY - 1)
        firstTimeOfDate = my_datetime.getFirstDayOfPrevMonth(importLastDay)
        firstTimeOfDateStr = my_datetime.dateTimeToStr(firstTimeOfDate, '%Y-%m-%d')
        data = get_all_employee_empty_salary_monthly(firstTimeOfDateStr)
        return data

    def updateEmployeeSalaryDaylySyncStatus(self, _employee_dict):
        return update_employee_salary_day_sync_status(_employee_dict)

    def updateEmployeeSalaryMonthSyncStatus(self, _employee_dict):
        return update_employee_salary_month_sync_status(_employee_dict)
