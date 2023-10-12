from datetime import datetime
from django.conf import settings as project_settings
from ...configs.service_api_config import SERVICE_CONFIG
from core.helpers.helper import call_api
from core.helpers import global_variable
from core.helpers import my_datetime

APP_ENV = project_settings.APP_ENVIRONMENT
PROFILE_API = SERVICE_CONFIG["profile_api"]


def get_employee_from_email(email, fields=None):
    if fields is None:
        fields = ["code", "email"]
    try:
        host = PROFILE_API[f"base_http_{APP_ENV}"]
        func = PROFILE_API["get_employee_from_email"]["func"]
        method = PROFILE_API["get_employee_from_email"]["method"]

        request_data = {
            "email": email,
            "fields": fields
        }
        data = call_api(host=host, func=func, method=method, data=request_data)
        if data and data.get("statusCode", -1) == 1:
            return data.get("data", None)
        else:
            raise ValueError(f"roi vao case data=null hoac statusCode khac 1, data la: {data}")
    except Exception as ex:
        print(f"{datetime.now()} >> get_employee_from_email >> {ex}")
        return None


def get_all_employee_empty_salary_daily(first_time_of_date):
    try:
        if not my_datetime.checkDatetimeFormat(first_time_of_date, "%Y-%m-%d"):
            raise ValueError("định dạng first_time_of_date không hợp lệ!")

        host = PROFILE_API[f"base_http_{APP_ENV}"]
        func = PROFILE_API["get_all_employee_empty_salary_daily"]["func"]
        method = PROFILE_API["get_all_employee_empty_salary_daily"]["method"]

        request_data = {
            "statusWorking": 1,
            "jobTitle": global_variable.SALARY_JOB_TITLE,
            "firstTimeOfDate": first_time_of_date
        }
        data = call_api(host=host, func=func, method=method, data=request_data)
        if data and data.get("statusCode", -1) == 1:
            return data.get("data", [])
        else:
            raise ValueError(f"roi vao case data=[] hoac statusCode khac 1, data la: {data}")
    except Exception as ex:
        print(f"{datetime.now()} >> get_all_employee_empty_salary_daily >> {ex}")
        return []


def get_all_employee_empty_salary_monthly(first_time_of_date):
    try:
        if not my_datetime.checkDatetimeFormat(first_time_of_date, "%Y-%m-%d"):
            raise ValueError("định dạng first_time_of_date không hợp lệ!")

        host = PROFILE_API[f"base_http_{APP_ENV}"]
        func = PROFILE_API["get_all_employee_empty_salary_monthly"]["func"]
        method = PROFILE_API["get_all_employee_empty_salary_monthly"]["method"]

        request_data = {
            "statusWorking": 1,
            "jobTitle": global_variable.SALARY_JOB_TITLE,
            "firstTimeOfDate": first_time_of_date
        }
        data = call_api(host=host, func=func, method=method, data=request_data)
        if data and data.get("statusCode", -1) == 1:
            return data.get("data", [])
        else:
            raise ValueError(f"roi vao case data=[] hoac statusCode khac 1, data la: {data}")
    except Exception as ex:
        print(f"{datetime.now()} >> get_all_employee_empty_salary_monthly >> {ex}")
        return []


def update_employee_salary_day_sync_status(_employee_dict):
    try:
        host = PROFILE_API[f"base_http_{APP_ENV}"]
        func = PROFILE_API["update_employee_salary_day_sync_status"]["func"]
        method = PROFILE_API["update_employee_salary_day_sync_status"]["method"]

        request_data = {
            "employees": _employee_dict
        }

        data = call_api(host=host, func=func, method=method, data=request_data)
        if data and data.get("statusCode", -1) == 1:
            return True
        else:
            raise ValueError(
                f"Loi khi cap nhat salary_daily_date_last_sync >> mypt-profile-api >> "
                f"update_employee_salary_day_sync_status")
    except Exception as ex:
        print(f"{datetime.now()} >> update_employee_salary_day_sync_status >> {ex}")
        return False


def update_employee_salary_month_sync_status(_employee_dict):
    try:
        host = PROFILE_API[f"base_http_{APP_ENV}"]
        func = PROFILE_API["update_employee_salary_month_sync_status"]["func"]
        method = PROFILE_API["update_employee_salary_month_sync_status"]["method"]

        request_data = {
            "employees": _employee_dict
        }

        data = call_api(host=host, func=func, method=method, data=request_data)
        if data and data.get("statusCode", -1) == 1:
            return True
        else:
            raise ValueError(
                f"Loi khi cap nhat salary_monthly_date_last_sync >> mypt-profile-api >> "
                f"update_employee_salary_month_sync_status")
    except Exception as ex:
        print(f"{datetime.now()} >> update_employee_salary_month_sync_status >> {ex}")
        return False
