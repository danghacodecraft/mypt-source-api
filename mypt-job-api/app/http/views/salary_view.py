from rest_framework.viewsets import ViewSet
from django.db import transaction
from django.db.models import Max, Count
from project.throttling import (
    SalaryUserRateThrottle,
    SalaryCronCallUserRateThrottle
)
from core.helpers import auth_session_handler as authSessionHandler
from core.helpers.response import *
from core.helpers.my_datetime import *
from ..serializers.salary_daily_serializer import *
from ..serializers.salary_real_serializer import *
from http.validations.salary_validate import (
    SalaryDailyValidate,
    SalaryMonthlyValidate
)
from http.apis.inside_api import *
from http.apis.profile_api import (
    get_employee_from_email
)
from datetime import datetime

def get_contract_email_from_branch(branch="PNC"):
    configs = SalaryConfigsSerializer.getContentByKey("SALARY_CONFIGS")

    if not empty(configs):
        if branch and branch == "PNC":
            return configs.get('contact_email', SALARY_CONTRACT_MAIL["PNC"]).capitalize()
        elif branch and branch == "TIN":
            return configs.get('contact_email_tin', SALARY_CONTRACT_MAIL["TIN"]).capitalize()
    return "---"


class SalaryView(ViewSet):
    throttle_classes = []

    moneyUnit = 'đ'
    otpTimeoutCacheKey = 'otp:empCode:timeRemaining'
    salary_explain = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        configs = SalaryConfigsSerializer.getContentByKey('SALARY_CONFIGS')
        self.salary_explain = SalaryConfigsSerializer.getContentByKey('SALARY_EXPLAIN')
        self.isRemoveSalaryDailyDuplicate = configs.get("is_remove_salary_daily_duplicate", 0)
        self.isRemoveSalaryDailyTotalDuplicate = configs.get("is_remove_salary_daily_total_duplicate", 0)
        self.isRemoveSalaryMonthlyDuplicate = configs.get("is_remove_salary_monthly_duplicate", 0)
        self.salaryOnOffStatus = configs.get("salary_on_off_status", 1)
        self.monthAfterNoDisplaySalary = configs.get("month_after_no_display_salary", 8)
        self.yearAfterNoDisplaySalary = configs.get("year_after_no_display_salary", 2023)

        if not empty(configs):
            self.moneyUnit = configs.get('money_unit', self.moneyUnit)
        print("====Salary===")

    def get_throttles(self):
        if self.action in ["get_salary_provisional_by_date",
                           "get_salary_formula_by_month",
                           "get_salary_real_by_month"]:
            return [SalaryUserRateThrottle()]
        elif self.action in ["sync_salary_inside_data_daily",
                             "sync_salary_inside_data_monthly",
                             "remove_salary_daily_before_sync_date",
                             "remove_salary_monthly_and_update_last_sync_date",
                             "remove_duplicate_salary_daily",
                             "remove_duplicate_salary_daily_total",
                             "remove_duplicate_salary_monthly"]:
            return [SalaryCronCallUserRateThrottle()]
        return self.throttle_classes

    def checkUserInfo(self, request):
        user_info = authSessionHandler.get_user_token(request)
        if empty(user_info):
            return None
        # check user dang login co quyen Xem Lương hay ko
        userPersData = user_info["permissions"]
        if userPersData.get("ALL", None) is None and userPersData.get("XEM_LUONG", None) is None:
            return None
        user_info['realEmail'] = user_info.get('email', '')
        # Check thông tin dữ liệu giả
        try:
            fakeConfig = SalaryConfigsSerializer.getContentByKey('SALARY_EMPLOYEES_FAKE_INFO')
            employEmail = user_info.get('email', '')
            if not (empty(employEmail) or empty(fakeConfig)):
                if (employEmail in fakeConfig) and not empty(fakeConfig[employEmail]):
                    # lay thong tin employee tu service mypt-profile-api
                    employee = get_employee_from_email(fakeConfig[employEmail])
                    if employee and not empty(employee.get("code", None)):
                        user_info['empCode'] = employee['code']
                        user_info['email'] = fakeConfig[employEmail]
            print(f"[{datetime.now()}][salary] >> checkUserInfo >> userInfoFake: {user_info}")
        except Exception as ex:
            print(f"{datetime.now()} >> checkUserInfo >> {ex}")

        if empty(user_info.get('empCode', '')) or empty(user_info.get('email', '')):
            return None
        return user_info

    def get_salary_in_home(self, request):
        # Lấy thông tin lương
        salaryFromDay = ''
        salaryToDay = ''
        salaryTitle = ''
        salaryDetails = []
        moneyUnit = 'đ'
        totalSalary = 0

        # check user dang login co quyen Xem Lương hay ko
        user_info = self.checkUserInfo(request)
        if user_info is None:
            print(f"[{datetime.now()}][get_salary_in_home] User nay ko co quyen xem luong!")
            return response_data(status=5, message='Bạn không có quyền thao tác chức năng xem lương!', data=None)

        # user Id nay co quyen ALL hoac Xem Luong! Nen co the lay thong tin luong!
        try:
            configs = SalaryConfigsSerializer.getContentByKey('SALARY_CONFIGS')
            if not empty(configs):
                moneyUnit = configs.get('money_unit', moneyUnit)
            empCode = user_info.get('empCode', '')

            # Check user dang login co Employee Code hay ko, co thi moi tiep tuc lay thong tin Luong
            if not empty(empCode):
                # print("User " + str(project_global.authUserSessionData.get("userId")) + " co emp code : " +
                # empCode)
                char = '/'
                salaryToDay = my_datetime.curentDay(subDay=1, char=char)
                dateFilter = datetime.strptime(salaryToDay, '%d{}%m{}%Y'.format(char, char))
                salaryFromDay = dateFilter.strftime('01{}%m{}%Y'.format(char, char))
                redis_service = RedisService()
                cache = redis_service.redis_service
                salaryHomeCacheKey = '{}:{}'.format(SALARY_HOME_CACHE_KEY_NAME, empCode)
                salaryInfo = cache.get(salaryHomeCacheKey)
                if not empty(salaryInfo):
                    salaryInfo = json.loads(salaryInfo)
                    totalSalary = salaryInfo.get('salary_total', 0)
                    salaryDetails = salaryInfo.get('salary_details', [])
                    # print('salaryDetails: ', salaryDetails)
                if empty(totalSalary) or empty(salaryDetails):
                    salarySerializer = SalaryDailySerializer()
                    salaryInfo = salarySerializer.getHomeInfo(_employee_code=empCode, _year=dateFilter.year,
                                                              _month=dateFilter.month)
                    if not empty(salaryInfo):
                        totalSalary = salaryInfo.get('salary_total', 0)
                        salaryDetails = salaryInfo.get('salary_details', [])
                        if not empty(totalSalary) and not empty(salaryDetails):
                            cacheSalaryHomeTimeOut = SALARY_CACHE_DEFAULT_TIMEOUT
                            # cacheSalaryHomeTimeOut = my_datetime.getSecondFromNowToLastOfDay()
                            # Tính đến thời điểm cuối ngày
                            cache.set(salaryHomeCacheKey,
                                      json.dumps({
                                          'salary_total': totalSalary,
                                          'salary_details': salaryDetails
                                      }),
                                      cacheSalaryHomeTimeOut)
            salaryTitle = "Lương tạm tính từ ngày {} đến {}".format(salaryFromDay, salaryToDay)
        except Exception as ex:
            print('error: {}'.format(ex))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        salary = {
            "total": moneyFormat(_num=totalSalary, unit=' ' + moneyUnit),
            "salaryTitle": salaryTitle,
            "salaryDetails": salaryDetails,
        }
        return response_data(data=salary)

    def get_salary_provisional_overview(self, request):
        funcName = 'get_salary_provisional_overview'

        user_info = self.checkUserInfo(request)
        if not user_info:
            return response_data(status=5, message='Bạn không có quyền thao tác chức năng này!')

        empCode = user_info.get('empCode', '')
        empEmail = user_info.get('email', '')
        date = datetime.today() - timedelta(days=1)
        # dateFrom = '01/{}/{}'.format(date.month,date.year)
        # dateTo = date.strftime('%d/%m/%Y')
        description = 'Tổng quan lương tạm tính theo từng ngày'
        salaryTotal = 0
        salaryDetails = []
        header = None
        try:
            salarySerializer = SalaryDailySerializer()
            salaryData = salarySerializer.getAllDaySalaryOfEmployee(_employee_code=empCode, _employee_email=empEmail,
                                                                    _year=date.year, _month=date.month, _day=date.day)
            if not empty(salaryData):
                header = salaryData.get('salary_header', None)
                salaryTotal = salaryData.get('salary_total', 0)
                salaryDetails = salaryData.get('salary_details', [])
        except Exception as ex:
            print("[ERROR]:{}:{}".format(funcName, ex))
            salaryTotal = 0
            header = {
                "date": "Ngày",
                "total": "Tổng",
                "BasicSalary": "Lương bậc nghề",
                "SumProductivitySalary": "Lương sản phẩm",
                "SumQuantitySalary": "Lương CLDV"
            }
            salaryDetails = []

        contactEmail = get_contract_email_from_branch(user_info.get("branch", ""))
        try:
            salary_formula = self.salary_explain["luong_tam_tinh"]
            punish = self.salary_explain["tien_phat"]
        except:
            salary_formula = "---"
            punish = "---"

        data = {
            "contactEmail": contactEmail,
            "description": description,
            "subDescription": '',
            "salaryFormula": salary_formula,
            "punish": punish,
            "currencyUnit": self.moneyUnit,
            "salaryTotal": numberFormat(salaryTotal),
            "header": header,
            "body": salaryDetails
        }
        return response_data(data=data)

    def get_salary_provisional_by_date(self, request):
        funcName = 'get_salary_provisional_by_date'

        user_info = self.checkUserInfo(request)
        if not user_info:
            return response_data(status=5, message='Bạn không có quyền thao tác chức năng này!')
        inputData = request.data
        if empty(inputData.get('filter', {})):
            return response_error(5)
        dateFilter = inputData.get('filter', {}).get('date', '')
        if empty(dateFilter):
            return response_error(5)

        # # test lương ngày
        # empCode = '00191178'
        # empMail = 'phuongnam.tuongnh@fpt.net'
        # contactEmail = '---'

        empCode = user_info.get('empCode', '')
        if empty(empCode):
            return response_error(5)

        empMail = user_info.get('email', '')
        data = {}
        description = 'Chi tiết lương tạm tính '
        subDescription = ''
        contactEmail = get_contract_email_from_branch(user_info.get("branch", ""))
        salaryDetails = []
        salaryTotal = 0

        # luong tam tinh cua ca thang
        if dateFilter == '*':
            char = '/'
            salaryToDay = curentDay(subDay=1, char=char)
            # ngay hom nay - 1
            dateFilter = datetime.strptime(salaryToDay, '%d{}%m{}%Y'.format(char, char))
            # ngay 1 -> ngay hom nay - 1
            salaryFromDay = dateFilter.strftime('01{}%m{}%Y'.format(char, char))
            description += 'tổng tháng'
            subDescription = '({}-{})'.format(salaryFromDay, salaryToDay)
            try:
                salary = SalaryDailySerializer()
                data = salary.getSalaryOfEmployeeByDate(_employee_code=empCode, _year=dateFilter.year,
                                                        _month=dateFilter.month, _day=0, _employee_email=empMail)
                if not empty(data):
                    salaryTotal = data.get('salary_total', 0)
                    salaryDetails = data.get('salary_details', [])
            except Exception as ex:
                print("[ERROR]:{}:{}".format(funcName, ex))
        else:
            try:
                dateFilter = strToDate(dateFilter, '%d/%m/%Y')
            except:
                return response_error(5)
            if empty(dateFilter):
                return response_error(5)
            description += 'theo ngày'
            # chỉ cho lấy dữ liệu của ngày 01-> T-1
            if today() > dateFilter > getLastDayOfPrevMonth(getDate(-1)):
                try:
                    salary = SalaryDailySerializer()
                    data = salary.getSalaryOfEmployeeByDate(_employee_code=empCode, _year=dateFilter.year,
                                                            _month=dateFilter.month, _day=dateFilter.day,
                                                            _employee_email=empMail)
                    if not empty(data):
                        salaryTotal = data.get('salary_total', 0)
                        salaryDetails = data.get('salary_details', [])
                except Exception as ex:
                    print("[ERROR]:{}:{}".format(funcName, ex))

        try:
            salary_formula = self.salary_explain["luong_tam_tinh"]
            punish = self.salary_explain["tien_phat"]
        except:
            salary_formula = "---"
            punish = "---"

        data = {
            "contactEmail": contactEmail,
            "description": description,
            "subDescription": subDescription,
            "salaryFormula": salary_formula,
            "punish": punish,
            "currencyUnit": self.moneyUnit,
            "salaryTotal": numberFormat(salaryTotal),
            "salaryDetails": salaryDetails
        }
        return response_data(data)

    def get_salary_formula_by_month(self, request):
        user_info = self.checkUserInfo(request)
        if not user_info:
            return response_data(status=5, message='Bạn không có quyền thao tác chức năng này!')

        empCode = user_info.get('empCode', '')
        empMail = user_info.get('email', '')
        realEmail = str(user_info.get('realEmail', ''))
        contactEmail = get_contract_email_from_branch(user_info.get("branch", ""))
        description = 'Chi tiết lương công thức'
        salaryTotal = 0
        salaryDetails = []
        monthFormat = '%m/%Y'

        try:
            salary_formula = self.salary_explain["luong_cong_thuc"]
            punish = self.salary_explain["tien_phat"]
        except:
            salary_formula = "---"
            punish = "---"

        # -------------------- Start account test ----------------------------------------------------------------------
        # check account test
        if self.salaryOnOffStatus == 0:
            fake_email = SalaryConfigsSerializer.getContentByKey('SALARY_EMPLOYEES_FAKE_INFO')
            fake_email = [e for e, _ in fake_email.items()]
            if realEmail.lower() not in fake_email:
                data = {
                    "contactEmail": f" {contactEmail} ",
                    "description": description,
                    "subDescription": '',
                    "salaryFormula": salary_formula,
                    "punish": punish,
                    "currencyUnit": self.moneyUnit,
                    "salaryTotal": "0",
                    "salaryDetails": []
                }
                return response_data(data=data, message=text_pending_salaray)
        # ------------------------ End account test  -------------------------------------------------------------------

        inputData = request.data
        if empty(inputData.get('filter', {})):
            return response_error(5)
        dateFilter = inputData.get('filter', {}).get('month', '')
        if empty(dateFilter):
            return response_error(5)

        try:
            dateFilter = strToDate(_str=dateFilter, _str_format=monthFormat)
        except:
            return response_error(5)
        if empty(dateFilter):
            return response_error(5)

        if getPrevMonth(today()) > dateFilter > getDateOfNextYear(today(), -2):
            salary = SalaryDailySerializer()
            if dateFilter < datetime(self.yearAfterNoDisplaySalary, self.monthAfterNoDisplaySalary, 1):
                # data = salary.getSalaryOfEmployeeByMonth(_employee_code=empCode, _year=dateFilter.year,
                #                                          _month=dateFilter.month, _employee_email=empMail)
                return response_data(status=1, message=text_fail_salary, data={
                    "contactEmail": f" {contactEmail} ",
                    "description": description,
                    "subDescription": '',
                    "salaryFormula": salary_formula,
                    "punish": punish,
                    "currencyUnit": self.moneyUnit,
                    "salaryTotal": numberFormat(salaryTotal),
                    "salaryDetails": salaryDetails
                    })

            data = salary.getSalaryOfEmployeeByMonth(_employee_code=empCode, _year=dateFilter.year,
                                                     _month=dateFilter.month, _employee_email=empMail)
            if not empty(data):
                salaryTotal = data.get('salary_total', 0)
                salaryDetails = data.get('salary_details', [])

        return response_data(data={
            "contactEmail": f" {contactEmail} ",
            "description": description,
            "subDescription": '',
            "salaryFormula": salary_formula,
            "punish": punish,
            "currencyUnit": self.moneyUnit,
            "salaryTotal": numberFormat(salaryTotal),
            "salaryDetails": salaryDetails if salaryTotal != 0 else NONE_SALARY_FORMULA_MONTHLY
        })

    def get_salary_real_by_month(self, request):
        funcName = 'get_salary_real_by_month'

        user_info = self.checkUserInfo(request)
        if not user_info:
            return response_data(status=5, message='Bạn không có quyền thao tác chức năng này!')

        empCode = user_info.get('empCode', '')
        empEmail = user_info.get('email', '')
        inputData = request.data
        if empty(inputData.get('filter', {})):
            return response_error(5)
        dateFilter = inputData.get('filter', {}).get('month', '')
        if empty(dateFilter):
            return response_error(5)
        monthFormat = '%m/%Y'
        description = 'Chi tiết lương hạch toán'
        dateFilter = strToDate(_str=dateFilter, _str_format=monthFormat)
        contactEmail = get_contract_email_from_branch(user_info.get("branch", ""))
        if empty(dateFilter):
            return response_error(5)
        salarySerializer = SalaryRealSerializer()
        salaryData = salarySerializer.getSalaryByMonth(_employee_mail=empEmail, _year=dateFilter.year,
                                                       _month=dateFilter.month)

        try:
            salary_formula = self.salary_explain["luong_hach_toan"]
            punish = self.salary_explain["tien_phat"]
        except:
            salary_formula = "---"
            punish = "---"

        data = {
            "contactEmail": f" {contactEmail} ",
            "description": description,
            "subDescription": '',
            "salaryFormula": salary_formula,
            "punish": punish,
            "currencyUnit": self.moneyUnit,
            "salaryTotal": salaryData.get('salary_total', '0'),
            "salaryDetails": salaryData.get('salary_details', [])
        }
        # chỗ này trả về message text fail theo định dạng html cho mobile vì mobile yêu cầu
        if data["salaryTotal"] == "0" and data["salaryDetails"] is None or data["salaryDetails"] == []:
            data["salaryDetails"] = NONE_SALARY_REAL_MONTHLY
            return response_data(data=data)

        return response_data(data)

    # Api Sync dữ liệu inside lương tạm tính
    def sync_salary_inside_data_daily(self, request):
        funcName = 'sync_salary_inside_data_daily'
        print('[{}] START'.format(funcName))
        res = {
            'total': []
        }
        salarySerializer = SalaryDailySerializer()
        # Lấy ra danh sách employee cần sync lương
        data = salarySerializer.getAllEmployeeEmptySalaryDaily()

        if len(data) < 1:
            return response_data(5, message='Employee not found')
        stop = 1
        maxStop = request.data.get('stop_row_count', 100000)
        update_salary_daily_date_last_sync_dict = {}

        for employee in data:
            empCode = employee.get('emp_code', None)
            empEmail = employee.get('email', None)
            if empty(empCode) or empty(empEmail):
                print('[{}][{}] error null info employee'.format(datetime.now(), funcName))
                continue
            dateLastUpdateStr = employee.get('salary_daily_date_last_sync', None)
            if dateLastUpdateStr:
                dateLastUpdate = strToDate(dateLastUpdateStr, "%Y-%m-%d")
            else:
                dateLastUpdate = None

            dateUpdate = getDate(-1)
            dateStart = 1
            dateEnd = dateUpdate.day + 1

            if not empty(dateLastUpdate):
                # Xét xem ngày cuối update nếu < ngày hiện tại -1 thì gọi api update
                dateLastUpdate = createDatetime(dateLastUpdate.year, dateLastUpdate.month, dateLastUpdate.day)
                dateUpdate = getDate(-1)
                if dateLastUpdate < dateUpdate:
                    if (dateLastUpdate.year == dateUpdate.year) and (dateLastUpdate.month == dateUpdate.month):
                        dateStart = dateLastUpdate.day
                else:
                    continue
            print('[{}][{}] processing employee {} from {}-{}-{} to {}-{}-{}'.format(datetime.now(),
                                                                                     funcName, empCode,
                                                                                     dateUpdate.year,
                                                                                     dateUpdate.month, dateStart,
                                                                                     dateUpdate.year, dateUpdate.month,
                                                                                     dateUpdate.day))
            # Update từ đầu tháng đến hiện tại
            lastDateSuccess = dateStart
            i = dateStart
            while i < dateEnd:
                # Kiểm tra có dữ liệu chưa trước khi gọi qua inside
                try:
                    empSalary = SalaryDaily.objects.filter(employee_code=empCode, year_calculate=dateUpdate.year,
                                                           month_calculate=dateUpdate.month, day_calculate=i).first()
                    if not empty(empSalary):
                        lastDateSuccess = i
                    else:
                        update = salarySerializer.syncInsideData(empCode, empEmail, dateUpdate.year, dateUpdate.month,
                                                                 i)
                        if update.get('status', False):
                            dateStr = '{}-{}-{}'.format(dateUpdate.year, dateUpdate.month, i)
                            if dateStr in res:
                                res[dateStr].append(empCode)
                            else:
                                res[dateStr] = [empCode]
                            lastDateSuccess = i
                        else:
                            # Sau 6 giờ sáng mà gọi lấy dữ liệu ngày trước vẫn chưa có
                            if (i < dateUpdate.day or (
                                    i == dateUpdate.day and dateUpdate.hour > SALARY_HOUR_SYNC_DAILY)):
                                lastDateSuccess = i
                            print('[{}][{}] employee {} Sync fail which date= {}'.format(datetime.now(), funcName,
                                                                                         empCode, i))
                    lastDateSuccess = i
                except Exception as ex:
                    print(
                        '[{}][{}] employee {}, day={} Sync daily error= {}'.format(datetime.now(), funcName, empCode, i,
                                                                                   ex))
                i += 1
            print('[{}][{}] employee {}, Update datetime last syns  {}'.format(datetime.now(), funcName, empCode,
                                                                               lastDateSuccess))
            # salarySerializer.updateEmployeeSalaryDaylySyncStatus([empCode],
            #                                                      createDatetime(dateUpdate.year, dateUpdate.month,
            #                                                                     lastDateSuccess))
            update_salary_daily_date_last_sync_dict[empCode] = createDatetime(dateUpdate.year,
                                                                              dateUpdate.month,
                                                                              lastDateSuccess) \
                .strftime("%Y-%m-%d")

            # Update daily total
            dateTo = getDate(-1)
            try:
                dateFrom = createDatetime(dateTo.year, dateTo.month, 1)
                updateTotal = salarySerializer.syncInsideDataDailyTotal(empCode, empEmail, dateFrom, dateTo)
                if not updateTotal.get('status', False):
                    print('[{}] employee {} Sync daily total fail'.format(funcName, empCode))
                else:
                    res['total'].append(empCode)
            except Exception as ext:
                print('[{}] employee {} Update daily total day to= {} error: {}'.format(funcName, empCode, dateTo, ext))
            stop += 1
            if stop > maxStop:
                break
        salarySerializer.updateEmployeeSalaryDaylySyncStatus(update_salary_daily_date_last_sync_dict)
        return response_data(res)

    # Api Sync dữ liệu inside lương công thức
    def sync_salary_inside_data_monthly(self, request):
        funcName = 'sync_salary_inside_data_monthly'
        print('[{}] START'.format(funcName))
        res = {}
        salarySerializer = SalaryDailySerializer()
        # Lấy ra danh sách employee cần sync lương
        data = salarySerializer.getAllEmployeeEmptySalaryMonthly()

        if len(data) < 1:
            return response_data(5, message='Employee not found')
        maxStop = request.data.get('stop_row_count', 100000)
        yearStart = request.data.get('year_start', 2022)
        monthStart = request.data.get('month_start', 1)
        stop = 1
        update_salary_monthly_date_last_sync_dict = {}

        for employee in data:
            empCode = employee.get('emp_code', None)
            empEmail = employee.get('email', None)
            if empty(empCode) or empty(empEmail):
                print('[{}][{}] error null info employee'.format(datetime.now(), funcName))
                continue
            dateLastUpdateStr = employee.get('salary_monthly_date_last_sync', None)
            if dateLastUpdateStr:
                dateLastUpdate = strToDate(dateLastUpdateStr, "%Y-%m-%d")
            else:
                dateLastUpdate = None

            dateLastSync = getDate(
                -SALARY_DAY_IMPORT_MONTHLY - 1)
            # Vì ngày 13 hàng tháng mới có lương, nên nếu chưa tới ngày thì không cần lấy dữ liệu của tháng trước
            dateUpdate = createDatetime(dateLastSync.year, dateLastSync.month, 1)
            monthEnd = getPrevMonth(dateUpdate).month

            if not empty(dateLastUpdate):
                # Xét xem tháng cuối update nếu < tháng hiện tại -1 thì gọi api update
                dateLastUpdate = createDatetime(dateLastUpdate.year, dateLastUpdate.month, dateLastUpdate.day)
                if dateLastUpdate < dateUpdate:
                    yearStart = dateLastUpdate.year
                    monthStart = dateLastUpdate.month
                    if dateLastUpdate.year == dateUpdate.year:
                        monthStart = dateLastUpdate.month
                else:
                    continue

            # Update từ đầu tháng đến hiện tại
            lastMonthSuccess = monthStart
            i = monthStart
            j = yearStart
            configs = SalaryConfigsSerializer.getContentByKey('SALARY_CONFIGS')
            salaryEndDayUpdate = configs.get('salary_day_stop_update', SALARY_END_DAY_IMPORT_MONTHLY)

            date_time_sync_success = None
            while j <= dateUpdate.year:
                while i <= 12 and (createDatetime(j, i, 1) < dateUpdate):
                    try:
                        update = salarySerializer.syncInsideMonthlyData(_employee_code=empCode,
                                                                        _employee_email=empEmail,
                                                                        _year=j,
                                                                        _month=i)
                        if update.get('status', False):
                            dateStr = '{}-{}'.format(j, i)
                            if dateStr in res:
                                res[dateStr].append(empCode)
                            else:
                                res[dateStr] = [empCode]
                            lastMonthSuccess = i
                        else:
                            if (i < dateUpdate.month or (
                                    i == dateUpdate.month and dateUpdate.day > salaryEndDayUpdate)):
                                # Sau ngày 16 hàng tháng mà gọi lấy dữ liệu lương tháng trước vẫn chưa có
                                lastMonthSuccess = i

                        date_time_sync_success = f"{lastMonthSuccess}/{j}"
                    except Exception as ex:
                        print('[{}][{}] employee {} Sync fail with error: {}'.format(datetime.now(), funcName, empCode,
                                                                                     ex))
                    i += 1
                j += 1
                i = 1

            #
            if date_time_sync_success:
                month_year_success = date_time_sync_success.split("/")
                m_success = int(month_year_success[0])
                y_success = int(month_year_success[1])
                update_salary_monthly_date_last_sync_dict[empCode] = f"{y_success}-{m_success}-{1}"
            stop += 1
            if stop > maxStop:
                break

        # update thoi gian dong bo luong thang cua nhan vien
        salarySerializer.updateEmployeeSalaryMonthSyncStatus(update_salary_monthly_date_last_sync_dict)
        print('[{}][{}] END'.format(datetime.now(), funcName))
        return response_data(res)

    def remove_duplicate_salary_daily(self, request):
        if self.isRemoveSalaryDailyDuplicate == 1:
            data = request.data.copy()
            unique_fields = ["employee_code", "year_calculate", "month_calculate", "day_calculate"]

            if "dateFrom" in data and "dateTo" in data:
                filter_validate = SalaryDailyValidate(data=data)
                if not filter_validate.is_valid():
                    return response_data(status=4, message=list(filter_validate.errors.values())[0][0])
                validated_data = filter_validate.data
                date_from = strToDate(validated_data["dateFrom"], _str_format="%Y-%m-%d").date()
                date_to = strToDate(validated_data["dateTo"], _str_format="%Y-%m-%d").date()

                salary_daily_duplicates = SalaryDaily.objects.values(*unique_fields) \
                    .order_by() \
                    .filter(year_calculate=date_from.year,
                            month_calculate=date_from.month) \
                    .filter(day_calculate__range=[date_from.day, date_to.day]) \
                    .annotate(max_id=Max('salary_daily_id'), count_id=Count('salary_daily_id')) \
                    .filter(count_id__gt=1)
            else:
                prev_date = getDate(-1).date()
                salary_daily_duplicates = SalaryDaily.objects.values(*unique_fields) \
                    .order_by() \
                    .filter(year_calculate=prev_date.year,
                            month_calculate=prev_date.month,
                            day_calculate=prev_date.day) \
                    .annotate(max_id=Max('salary_daily_id'), count_id=Count('salary_daily_id')) \
                    .filter(count_id__gt=1)

            try:
                rows_success = []
                with transaction.atomic():
                    for salary_daily_duplicate in salary_daily_duplicates:
                        delete_result = SalaryDaily.objects \
                            .filter(**{x: salary_daily_duplicate[x] for x in unique_fields}) \
                            .exclude(salary_daily_id=salary_daily_duplicate['max_id']) \
                            .delete()

                        emp_code = salary_daily_duplicate["employee_code"]
                        day_calculate = salary_daily_duplicate["day_calculate"]
                        month_calculate = salary_daily_duplicate["month_calculate"]
                        year_calculate = salary_daily_duplicate["year_calculate"]
                        if delete_result[0] > 0:
                            row_success_str = f'REMOVE DUPLICATE SUCCESS => EmpCode: {emp_code}, date: {day_calculate}/{month_calculate}/{year_calculate}'
                        else:
                            row_success_str = f'REMOVE DUPLICATE FAILED => EmpCode: {emp_code}, date: {day_calculate}/{month_calculate}/{year_calculate} '
                        rows_success.append(row_success_str)
            except Exception as ex:
                print(f"{datetime.now()} >> remove_duplicate_salary_daily >> {ex}")
                return response_data(status=4, message=f"Lỗi: {ex}")
            else:
                return response_data(data=rows_success)
        else:
            return response_data(message="Api nay da block!")

    def remove_salary_monthly_and_update_last_sync_date(self, request):
        try:
            today_date = date.today()
            first_day_of_this_month = date(today_date.year, today_date.month, 1)
            last_month = first_day_of_this_month - timedelta(days=1)
            first_day_last_month = date(last_month.year, last_month.month, 1)
            # xóa db lương tháng và chỉnh sửa ngày sync đồng bộ lại lương
            with transaction.atomic():
                # EmployeesTb.objects.filter(status_working=1).update(salary_monthly_date_last_sync=first_day_last_month)

                SalaryMonthly.objects.filter(
                    year_calculate=first_day_last_month.year, month_calculate=first_day_last_month.month).delete()

            return response_data(message='Xóa lương tháng để đồng bộ lại thành công', status=1)
        except Exception as ex:
            print(f"{datetime.now()} >> remove_salary_monthly_and_update_last_sync_date >> {ex}")
            return response_data(status=4, message=f"Lỗi: {ex}")

    def remove_salary_daily_before_sync_date(self, request):
        target_date = getDate(-1)
        date_today = date.today()
        date_now = datetime(date_today.year, date_today.month, date_today.day, 5, 0)

        try:
            SalaryDaily.objects.filter(day_calculate=target_date.day, month_calculate=target_date.month,
                                       year_calculate=target_date.year, date_row_created__lt=date_now
                                       ).delete()
            return response_data(message=f"Xóa thành công người xem data ngày trước {date_now}")

        except Exception as ex:
            print(f"{datetime.now()} >> remove_duplicate_salary_daily >> {ex}")
            return response_data(status=4, message=f"Lỗi: {ex}")

    def remove_duplicate_salary_daily_total(self, request):
        if self.isRemoveSalaryDailyTotalDuplicate == 1:
            data = request.data.copy()
            unique_fields = ["employee_code", "year_calculate", "month_calculate", "day_last_calculate"]

            if "dateFrom" in data and "dateTo" in data:
                filter_validate = SalaryDailyValidate(data=data)
                if not filter_validate.is_valid():
                    return response_data(status=4, message=list(filter_validate.errors.values())[0][0])
                validated_data = filter_validate.data
                date_from = strToDate(validated_data["dateFrom"], _str_format="%Y-%m-%d").date()
                date_to = strToDate(validated_data["dateTo"], _str_format="%Y-%m-%d").date()

                salary_daily_total_duplicates = SalaryDailyTotal.objects.values(*unique_fields) \
                    .order_by() \
                    .filter(year_calculate=date_from.year,
                            month_calculate=date_from.month) \
                    .filter(day_last_calculate__range=[date_from.day, date_to.day]) \
                    .annotate(max_id=Max('salary_daily_total_id'), count_id=Count('salary_daily_total_id')) \
                    .filter(count_id__gt=1)
            else:
                prev_date = getDate(-1).date()
                salary_daily_total_duplicates = SalaryDailyTotal.objects.values(*unique_fields) \
                    .order_by() \
                    .filter(year_calculate=prev_date.year,
                            month_calculate=prev_date.month,
                            day_last_calculate=prev_date.day) \
                    .annotate(max_id=Max('salary_daily_total_id'), count_id=Count('salary_daily_total_id')) \
                    .filter(count_id__gt=1)

            try:
                rows_success = []
                with transaction.atomic():
                    for salary_daily_total_duplicate in salary_daily_total_duplicates:
                        delete_result = SalaryDailyTotal.objects \
                            .filter(**{x: salary_daily_total_duplicate[x] for x in unique_fields}) \
                            .exclude(salary_daily_total_id=salary_daily_total_duplicate['max_id']) \
                            .delete()

                        emp_code = salary_daily_total_duplicate["employee_code"]
                        day_last_calculate = salary_daily_total_duplicate["day_last_calculate"]
                        month_calculate = salary_daily_total_duplicate["month_calculate"]
                        year_calculate = salary_daily_total_duplicate["year_calculate"]
                        if delete_result[0] > 0:
                            row_success_str = f'REMOVE DUPLICATE SUCCESS => EmpCode: {emp_code}, date: {day_last_calculate}/{month_calculate}/{year_calculate}'
                        else:
                            row_success_str = f'REMOVE DUPLICATE FAILED => EmpCode: {emp_code}, date: {day_last_calculate}/{month_calculate}/{year_calculate} '
                        rows_success.append(row_success_str)
            except Exception as ex:
                print(f"{datetime.now()} >> remove_duplicate_salary_daily_total >> {ex}")
                return response_data(status=4, message=f"Lỗi: {ex}")
            else:
                return response_data(data=rows_success)
        else:
            return response_data(message="Api này đã bị block!")

    def remove_duplicate_salary_monthly(self, request):
        if self.isRemoveSalaryMonthlyDuplicate == 1:
            data = request.data.copy()
            unique_fields = ["employee_code", "year_calculate", "month_calculate"]

            filter_validate = SalaryMonthlyValidate(data=data)
            if not filter_validate.is_valid():
                default_date = getFirstDayOfPrevMonth(datetime.now()).strftime("%Y-%m-%d")
                validated_data = {
                    "dateFrom": default_date,
                    "dateTo": default_date
                }
            else:
                validated_data = filter_validate.data
            date_from = strToDate(validated_data["dateFrom"], _str_format="%Y-%m-%d").date()
            date_to = strToDate(validated_data["dateTo"], _str_format="%Y-%m-%d").date()

            try:
                salary_monthly_duplicates = SalaryMonthly.objects.values(*unique_fields) \
                    .order_by() \
                    .filter(year_calculate=date_from.year,
                            month_calculate__range=[date_from.month, date_to.month]) \
                    .annotate(max_id=Max('salary_monthly_id'), count_id=Count('salary_monthly_id')) \
                    .filter(count_id__gt=1)

                rows_success = []
                with transaction.atomic():
                    for salary_monthly_duplicate in salary_monthly_duplicates:
                        delete_result = SalaryMonthly.objects \
                            .filter(**{x: salary_monthly_duplicate[x] for x in unique_fields}) \
                            .exclude(salary_monthly_id=salary_monthly_duplicate['max_id']) \
                            .delete()

                        emp_code = salary_monthly_duplicate["employee_code"]
                        month_calculate = salary_monthly_duplicate["month_calculate"]
                        year_calculate = salary_monthly_duplicate["year_calculate"]
                        if delete_result[0] > 0:
                            row_success_str = f'REMOVE DUPLICATE SUCCESS => EmpCode: {emp_code}, date: {month_calculate}/{year_calculate}'
                        else:
                            row_success_str = f'REMOVE DUPLICATE FAILED => EmpCode: {emp_code}, date: {month_calculate}/{year_calculate} '
                        rows_success.append(row_success_str)
            except Exception as ex:
                print(f"{datetime.now()} >> remove_duplicate_salary_monthly >> {ex}")
                return response_data(status=4, message=f"Lỗi: {ex}")
            else:
                return response_data(data=rows_success)
        else:
            return response_data(message="Api này đã bị block!")
