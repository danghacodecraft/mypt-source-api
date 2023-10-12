from django.conf import settings
SERVICE_CONFIG = {
    "survey": {
        "base_http": "http://survey.fpt.vn/",
        "getDetailPointEmp": "api/v1/get-detail-point-emp",
        "method": "POST"
    },
    "SETTING": {
        "show_hide_tab": {
            "production": "http://myptpdx-api.fpt.net/mypt-setting-api/v1/",
            "staging": "http://myptpdx-api-stag.fpt.net/mypt-setting-api/v1/",
            "local": "http://mypt.local/mypt-setting-api/v1/",
            # "host":"http://mypt.local:8000/mypt-setting-api/v1/",
            "func": "show-hide-user-home-tab",
            "method": "POST"
        }
    },
    "COMPANY": {
        "production": "http://mypt-company-api/mypt-company-api/v1/",
        "staging": "http://mypt-company-api-staging/mypt-company-api/v1/",
        "local": "http://mypt.local/mypt-company-api/v1/",
        # "host":"http://mypt.local:8080/mypt-company-api/v1/",
        "home_count_ptq": {
            "func": "home-count-ptq",
            "method": "GET"
        },
        "get_ptq_types_from_redis": {
            "func": "get-ptq-types-from-redis",
            "method": "POST"
        },
        "get_ptq_from_email": {
            "func": "get-ptq-from-email",
            "method": "POST"
        }
    },
    "survey": {
        "production": "http://mypt-surveys-api/mypt-surveys-api/v1/",
        "staging": "http://mypt-surveys-api-staging/mypt-surveys-api/v1/",
        "local": "http://127.0.0.1:4000/mypt-surveys-api/v1/",
        "scrutiny": {
            "func": "labor-safety/scrutiny",
            "method": "get"
        }
    }
}

def get_api_info(service_name: str, function_name: str) -> dict:
    if service_name not in SERVICE_CONFIG:
        raise Exception(f'{service_name} service information has not been declared')
    
    if function_name not in SERVICE_CONFIG[service_name]:
        raise Exception(f'{function_name} function information has not been declared')
    
    venv = settings.APP_ENVIRONMENT
    _func = "func"
    
    return {
        "url": f"{SERVICE_CONFIG[service_name][venv]}{SERVICE_CONFIG[service_name][function_name][_func]}",
        "method": SERVICE_CONFIG[service_name][function_name]["method"]
    }
