from django.conf import settings

SERVICE_CONFIG = {
    "survey": {
        "base_http": "http://survey.fpt.vn/",
        "getDetailPointEmp": "api/v1/get-detail-point-emp",
        "method": "POST"
    },
    "profile_api": {
        "base_http_local": "http://127.0.0.1:8001/mypt-profile-api/v1/",
        "base_http_staging": "http://mypt-profile-api-staging/mypt-profile-api/v1/",
        "base_http_production": "http://mypt-profile-api/mypt-profile-api/v1/",
        "get_employee_from_email": {
            "func": "get-employee-from-email",
            "method": "POST"
        },
        "get_all_employee_empty_salary_daily": {
            "func": "get-all-employee-empty-salary-daily",
            "method": "POST"
        },
        "get_all_employee_empty_salary_monthly": {
            "func": "get-all-employee-empty-salary-monthly",
            "method": "POST"
        },
        "update_employee_salary_day_sync_status": {
            "func": "update-employee-salary-day-sync-status",
            "method": "POST"
        },
        "update_employee_salary_month_sync_status": {
            "func": "update-employee-salary-month-sync-status",
            "method": "POST"
        }
    },
    "notification": {
        "base_http_local": "http://myptpdx-api-stag.fpt.net/mypt-notification-api/v2/",
        "base_http_staging": "http://mypt-notification-api-staging/mypt-notification-api/v2/",
        "base_http_production": "http://mypt-notification-api/mypt-notification-api/v2/",
        "send_one_noti": {
            "func": "send-one-noti",
            "method": "POST"
        }
    },
    "SCM":{
        "base_http_local": "http://ftelscmapistag.fpt.vn/api/ApiFIP/",
        "base_http_staging": "http://ftelscmapistag.fpt.vn/api/ApiFIP/",
        "base_http_production": "https://ftelscm.fpt.vn/api/ApiFIP/",
        "tools": {
            "func": "GetListInvItemBalanceEmployeeByEmail",
            "method": "POST"
        }
    },
    "logs":{
        "base_http_local": "http://localhost:8000/mypt-logs-api/v1/",
        "base_http_staging": "http://mypt-logs-api-staging/mypt-logs-api/v1/",
        "base_http_production": "http://mypt-logs-api/mypt-logs-api/v1/",
        "save_log": {
            "func": "save-log",
            "method": "POST"
        }
    }
}

SERVICE_CONFIG_SAVE_LOGS_API = {
    "service_name": "/mypt-job-api/v1/",
    # KPIS
    "get_kpi_result": {
        "func" : "get-kpi-result",
        "function_code": "KPIS",
        "action_code": "XEM_CHI_SO_KPIS"
    },
    "get_kpi_list_chart": {
        "func": "get-kpi-list-chart",
        "function_code": "KPIS",
        "action_code": [
            "XEM_KPI_DUNG_HEN_TK_BT",
            "XEM_KPI_SLA_TK_BT",
            "XEM_KPI_KH_2CL",
            "XEM_KPI_KH_3CL",
            "XEM_KPI_CLPS7N_TK_BT",
        ]
    },
    "get_kpi_detail_info": {
        "func": "get-kpi-detail-info",
        "function_code": "KPIS",
        "action_code": [
            "XEM_CHI_TIET_KPI_DUNG_HEN_TK_BT",
            "XEM_CHI_TIET_KPI_SLA_TK_BT",
            "XEM_CHI_TIET_KPI_KH_2CL",
            "XEM_CHI_TIET_KPI_KH_3CL",
            "XEM_CHI_TIET_KPI_CLPS7N_TK_BT",
        ]
    },
    "get_csat_list_chart": {
        "func": "get-csat-list-chart",
        "function_code": "KPIS",
        "action_code": [
            "XEM_DIEM_CSAT_DV",
            "XEM_DIEM_CSAT_NV",
        ]
    },
}

def get_api_info(service_name: str, function_name: str) -> dict:
    if service_name not in SERVICE_CONFIG:
        raise Exception(f'{service_name} service information has not been declared')
    
    if function_name not in SERVICE_CONFIG[service_name]:
        raise Exception(f'{function_name} function information has not been declared')
    
    venv = settings.APP_ENVIRONMENT
    _base = f"base_http_{venv}"
    _func = "func"
    
    return {
        "url": f"{SERVICE_CONFIG[service_name][_base]}{SERVICE_CONFIG[service_name][function_name][_func]}",
        "method": SERVICE_CONFIG[service_name][function_name]["method"]
    }
