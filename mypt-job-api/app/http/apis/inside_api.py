import datetime
from requests import request, exceptions, post
import json
from ...core.helpers.utils import *
from datetime import datetime
from ...core.entities.redis_service import RedisService
from threading import Thread
from ..models.salary_call_api_inside_histories import SalaryCallApiInsideHistories
from ..serializers.salary_configs_serializer import SalaryConfigsSerializer


class InsideApi:
    token = ''
    cache = {}
    cache_authen_key = INSIDE_API_CACHE_KEY_NAME + ':JwtToken'
    res = None

    def __init__(self):
        # print("InsideApi")
        self.cache = RedisService().redis_service
        configs = SalaryConfigsSerializer.getContentByKey("SALARY_CONFIGS")
        self.isDailySalarySync = configs.get("is_daily_salary_sync", 0)
        self.isMonthlySalarySync = configs.get("is_monthly_salary_sync", 0)
        # Check authen
        authenJwtToken = self.cache.get(self.cache_authen_key)
        if empty(authenJwtToken):
            self.authenticate()
        else:
            self.token = authenJwtToken

    def __del__(self):
        print('InsideApi DEstructor is called Manually')

    def saveLog(self):
        print('InsideApi saveLog start')
        logObject = SalaryCallApiInsideHistories()
        output = self.res
        curentTime = datetime.today()
        logObject.year_call_api = curentTime.year
        logObject.month_call_api = curentTime.month
        logObject.day_call_api = curentTime.day
        try:
            logObject.api_full_url = output.request.url
            logObject.http_status = output.status_code
            logObject.http_message = output.reason
            logObject.total_time = output.elapsed.total_seconds()
            logObject.response_headers = dict(output.headers)
            logObject.request_headers = dict(output.request.headers)
            logObject.api_method = output.request.method
        except Exception as ex:
            print('InsideApi Savelog Error: {}'.format(ex))
        try:
            input = json.loads(output.request.body)
            logObject.request_body = input
            logObject.employee_code = input.get('employee_code', '')
        except Exception as ex:
            print('InsideApi Savelog Error: {}'.format(ex))
            logObject.employee_code = '-1'
        try:
            response = json.loads(output.text)
            logObject.response_body = response
            status = response.get('succeeded', -1)
            if status:
                logObject.response_status = 1
            elif not status:
                logObject.response_status = 0
            else:
                logObject.response_status = -1
            logObject.response_message = response.get('message', None)
            logObject.response_error = response.get('errors', None)
        except Exception as ex:
            print('InsideApi Savelog Error: {}'.format(ex))
            logObject.response_body = output.text
            logObject.response_status = -1
            logObject.response_message = None
            logObject.response_error = None
        try:
            logObject.save()
        except Exception as ex:
            print('InsideApi Savelog Error: {}'.format(ex))
        print('InsideApi saveLog end')
        return 1

    def authenticate(self):
        apiUrl = 'https://iam.fpt.vn/auth/realms/fpt/protocol/openid-connect/token'
        inputParamsStr = {
            'client_id': 'salary_portal',
            'client_secret': 'XH7EIiguszuHT58o57w4UcH7pWIfS38r',
            'grant_type': 'client_credentials'
        }
        headersDict = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json"
        }
        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn:80"
        }
        self.res = responseObj = post(url=apiUrl, headers=headersDict, proxies=proxies, data=inputParamsStr, timeout=5)
        Thread(target=self.saveLog).start()
        if responseObj.status_code == 200:
            responseData = json.loads(responseObj.text)
            access_token = responseData.get('access_token', '')
            expires_in = responseData.get('expires_in', '')
            if empty(access_token) or empty(expires_in):
                print('INSIDE_API:AUTHENTICATION_FAILED: response.Data={}'.format(json.dumps(responseData)))
            else:
                self.token = access_token
                self.cache.set(self.cache_authen_key, access_token, expires_in)
        else:
            print('INSIDE_API:AUTHENTICATION_FAILED: status={}, message={}'.format(responseObj.status_code,
                                                                                   responseObj.reason))
            print(self.getFullInfo(responseObj))
        return True

    def salary_provisional(self, _employee_code, _from_date, _to_date):
        if empty(self.isDailySalarySync):
            return {
                'status': False,
                'message': 'Chức năng đồng bộ lương đã bị block!',
                'data': []
            }

        apiUrl = INSIDE_API_DOMAIN_BASE_URL + "equipment/api/v1/PartnerSalaryMyPT/Partner-Salary-Provisional-MyPT"
        inputParamsStr = json.dumps({
            "employee_code": _employee_code,
            "from_date": _from_date,
            "to_date": _to_date
        })
        headersDict = {
            "Content-Type": "application/json",
            'Authorization': 'Bearer {}'.format(self.token)
        }
        error = ''
        try:
            self.res = responseObj = request("POST", apiUrl, headers=headersDict, data=inputParamsStr,
                                             timeout=INSIDE_API_SALARY_CACHE_TIMEOUT)
            Thread(target=self.saveLog).start()
            if responseObj.status_code == 200:
                responseData = json.loads(responseObj.text)
                # thêm kiểm tra output
                status = responseData.get('Succeeded', None)
                message = responseData.get('Message', 'Success')
                error = responseData.get('Errors', {})
                data = responseData.get('Data', {})
                if status is None:
                    return {
                        'status': False,
                        'message': 'Error',
                        'data': self.getFullInfo(responseObj)
                    }
                elif not status:
                    return {
                        'status': status,
                        'message': message,
                        'data': error
                    }
                else:
                    res = {
                        'status': status,
                        'message': message,
                        'data': None
                    }
                    if message == 'no_data_found':
                        res['data'] = []
                    else:
                        res['data'] = data
                    return res
            else:
                return {
                    'status': False,
                    'message': 'Error',
                    'data': self.getFullInfo(responseObj)
                }
        except Exception as ex:
            error = str(ex)
            if isinstance(ex, exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("Call mypt-setting from mypt-auth :Connection Timeout")
            if isinstance(ex, exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("Call mypt-setting from mypt-auth :Connection Timeout")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        return {
            'status': False,
            'message': 'Error',
            'data': error
        }

    def getFullInfo(self, responseObj):
        return {
            "http_status": responseObj.status_code,
            'http_message': responseObj.reason,
            'total_time': responseObj.elapsed,
            'text': responseObj.text,
            'headers': responseObj.headers,
            'raw': responseObj.raw,
            'history': responseObj.history,
            'encoding': responseObj.encoding,
            'cookies': responseObj.cookies,
            'input': {
                'headers': responseObj.request.headers,
                'method': responseObj.request.method,
                'body': responseObj.request.body,
                'url': responseObj.request.url,
            }
        }

    def salary_month(self, _employee_code, _month):
        if empty(self.isMonthlySalarySync):
            return {
                'status': False,
                'message': 'Chức năng đồng bộ lương đã bị block!',
                'data': []
            }
        apiUrl = INSIDE_API_DOMAIN_PRODUCTION + "/tinpnc-salary/handlingpayroll/api/v1/PartnerSalaryMyPT/Partner-Month-Salary-MyPT"
        inputParamsStr = json.dumps({
            "employee_code": _employee_code,
            "month": _month
        })
        headersDict = {
            "Content-Type": "application/json",
            'Authorization': 'Bearer {}'.format(self.token)
        }
        try:
            self.res = responseObj = request("POST", apiUrl, headers=headersDict, data=inputParamsStr,
                                             timeout=INSIDE_API_SALARY_CACHE_TIMEOUT)
            Thread(target=self.saveLog).start()
            # api lương tháng mới từ inside đổi status success thành 201
            if responseObj.status_code in (200, 201):
                responseData = json.loads(responseObj.text)
                # thêm kiểm tra output
                status = responseData.get('succeeded', None)
                message = responseData.get('message', 'Success')
                error = responseData.get('errors', {})
                data = responseData.get('data', {})
                if status is None:
                    return {
                        'status': False,
                        'message': 'Error',
                        'data': self.getFullInfo(responseObj)
                    }
                elif not status:
                    return {
                        'status': status,
                        'message': message,
                        'data': error
                    }
                else:
                    res = {
                        'status': status,
                        'message': message,
                        'data': None
                    }
                    if message == 'no_data_found':
                        res['data'] = []
                    else:
                        res['data'] = data
                    return res
            else:
                return {
                    'status': False,
                    'message': 'Error',
                    'data': self.getFullInfo(responseObj)
                }
        except Exception as ex:
            error = str(ex)
            if isinstance(ex, exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("Call mypt-setting from mypt-auth :Connection Timeout")
            if isinstance(ex, exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("Call mypt-setting from mypt-auth :Connection Timeout")

        return {
            'status': False,
            'message': 'Error',
            'data': error
        }
