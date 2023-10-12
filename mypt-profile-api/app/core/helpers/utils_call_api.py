import pyshorteners
import json
from django.conf import settings as project_settings
from ..helpers.service_api import call_api
from ...configs.service_api_config import SERVICE_CONFIG


def call_api_shorten_link(url):
    proxies = {
        "http": "http://proxy.hcm.fpt.vn:80",
        "https": "http://proxy.hcm.fpt.vn:80"
    }
    # proxies = {
    #     "http": None,
    #     "https": "proxy.hcm.fpt.vn",
    # }
    s = pyshorteners.Shortener(proxies=proxies, verify=False, timeout=5)
    short_link = s.tinyurl.short(url)

    return short_link


def call_api_get_user_id_by_email(email):
    try:
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        response = call_api(
            host=SERVICE_CONFIG["auth-api"][app_env],
            func=SERVICE_CONFIG["auth-api"]["GetUserIdByEmail"],
            method=SERVICE_CONFIG["auth-api"]["method"],
            data={
                "email": email
            }
        )
        return json.loads(response)
    except:
        return None
