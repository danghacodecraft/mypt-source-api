SERVICE_CONFIG = {
    "survey": {
        "base_http": "http://survey.fpt.vn/",
        "getDetailPointEmp": "api/v1/get-detail-point-emp",
        "method": "POST"
    },
    "hr": {
        "base_http": "http://hrapi.fpt.vn/api/",
        "auth": "services/hub/Login",
        "method": "POST",
        "param": {
            "username": "pnc@hr.fpt.vn",
            "password": "!@#Pnc123",
            "rememberClient": "True"
        },
        "GetEmployeeInfo": "services/app/pnc/GetEmployeeInfo",
        "GetCheckinReport": "services/app/pnc/GetCheckinReport"
    },
    "auth-api": {
        "base_http_local": "http://127.0.0.1:8002/mypt-auth-api/v1/",
        "base_http_dev": "http://mypt-auth-api-dev/mypt-auth-api/v1/",
        "base_http_staging": "http://mypt-auth-api-staging/mypt-auth-api/v1/",
        "base_http_production": "http://mypt-auth-api/mypt-auth-api/v1/",
        "method": "POST",
        "GetUserDeviceInfoByEmail": "get-user-device-info-by-email",
        "GetUserIdByEmail": "get-user-id-by-email"
    },
    "checkin-api": {
        "base_http_local": "http://127.0.0.1:8003/mypt-checkin-api/v2/",
        "base_http_dev": "http://mypt-checkin-api-dev/mypt-checkin-api/v2/",
        "base_http_staging": "http://mypt-checkin-api-staging/mypt-checkin-api/v2/",
        "base_http_production": "http://mypt-checkin-api/mypt-checkin-api/v2/",
        "get_code": {
            "func": "get_info_checkin_from_emp_code",
            "method": "GET"
        }
    },
    "setting-api": {
        "base_http_local": "http://127.0.0.1:8006/mypt-setting-api/v1/",
        "base_http_dev": "http://mypt-setting-api-dev/mypt-setting-api/v1/",
        "base_http_staging": "http://mypt-setting-api-staging/mypt-setting-api/v1/",
        "base_http_production": "http://mypt-setting-api/mypt-setting-api/v1/",
        "get_code": {
            "func": "get-config",
            "method": "POST"
        }
    },
    "job-api": {
        "base_http_local": "http://127.0.0.1:8004/mypt-job-api/v1/",
        "base_http_dev": "http://mypt-job-api-dev/mypt-job-api/v1/",
        "base_http_staging": "http://mypt-job-api-staging/mypt-job-api/v1/",
        "base_http_production": "http://mypt-job-api/mypt-job-api/v1/",
        "get_salary_in_home": {
            "func": "get-salary-in-home",
            "method": "GET"
        }
    },
    "logs_api":{
        "base_http_local": "http://localhost:8000/mypt-logs-api/v1/",
        "base_http_staging": "http://mypt-logs-api-staging/mypt-logs-api/v1/",
        "base_http_production": "http://mypt-logs-api/mypt-logs-api/v1/",
        "save_log": {
            'func' : "save-log",
            "method" : "POST"
        }
    },
}

SERVICE_CONFIG_SAVE_LOGS_API = {
    "service_name": "/mypt-profile-api/v1/",
    "get_contracts": {
        "func" : "get-contracts",
        "function_code": "THONG_TIN_CUA_TOI",
        "action_code": "XEM_THONG_TIN_HOP_DONG"
    },
    "update_avatar": {
        "func" : "update-avatar",
        "function_code": "THONG_TIN_CUA_TOI",
        "action_code": "THAY_DOI_ANH_DAI_DIEN"
    },
    "get_application_info": {
        "func" : "get-application-info",
        "function_code": "THONG_TIN_CUA_TOI",
        "action_code": "XEM_THONG_TIN_APP"
    },
    "get_device_info": {
        "func" : "get-device-info",
        "function_code": "THONG_TIN_CUA_TOI",
        "action_code": "XEM_THONG_TIN_THIET_BI_DANG_KY_DIEM_DANH"
    },
}