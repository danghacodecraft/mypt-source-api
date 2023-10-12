SERVICE_CONFIG = {
    "survey":{
        "base_http": "http://survey.fpt.vn/",
        "getDetailPointEmp": "api/v1/get-detail-point-emp",
        "method": "POST"
    },
    "profile_api": {
        "base_http_local": "http://localhost:8001/mypt-profile-api/v1/",
        # "base_http_staging": "http://myptpdx-api-stag.fpt.net/mypt-profile-api/v1/",
        "base_http_staging": "http://mypt-profile-api-staging/mypt-profile-api/v1/",
        "base_http_production": "http://mypt-profile-api/mypt-profile-api/v1/",
        "get_list_avatar_from_list_email": {
            'func': "get-list-avatar-from-list-email",
            "method": "POST"
        },
        "get_list_email_pdx": {
            'func': 'get-list-email-pdx',
            "method": 'GET'
        },
        "get_features_roles_emails_improve_car": {
            'func': 'get-features-roles-emails-improve-car',
            "method": "GET"
        }
    },
    "FCM_API_DEEPLINK": {
        "base_http": "https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyAHUPGUFYhNlSokb7p7qQncIF2kWid1HuU",
        "method": "POST"
    },
    "NOTIFICATION": {
        "base_http_local": "http://mypt.local/mypt-notification-api/v1/",
        "base_http_staging": "http://mypt-notification-api-staging/mypt-notification-api/v1/",
        "base_http_production": "http://mypt-notification-api/mypt-notification-api/v1/",
        "send_noti": {
            'func': "send-one-noti",
            "method": "POST"
        }
    },
    "WEBKIT": {
        "staging": "https://mypt-webkit-stag.fpt.vn/improved-car/view/",
        "production": "https://webkit.mypt.vn/improved-car/view/"
    },
    "logs_api": {
        "base_http_local": "http://localhost:8000/mypt-logs-api/v1/",
        "base_http_staging": "http://mypt-logs-api-staging/mypt-logs-api/v1/",
        "base_http_production": "http://mypt-logs-api/mypt-logs-api/v1/",
        "save_log": {
            'func': "save-log",
            "method": "POST"
        }
    },
}

SERVICE_CONFIG_SAVE_LOGS_API = {
    "service_name": "/mypt-company-api/v1/",
    # QUAN_LY_XE_CAI_TIEN
    "get_list_blog_id": {
        "func": "list-idea?id=",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "XEM_CHI_TIET_BAI_VIET"
    },
    "get_list_blog": {
        "func": "list-idea",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "XEM_DANH_SACH_BAI_VIET"
    },
    "post_blog": {
        "func": "create-blogs",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "DANG_BAI_VIET"
    },
    "create_comment": {
        "func": "create-comment",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "COMMENT_BAI_VIET"
    },
    "detele_comment": {
        "func": "detele-comment",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "XOA_COMMENT"
    },
    "do_like": {
        "func": "do-like",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "THICH_BAI_VIET"
    },
    "post_rate": {
        "func": "do-rate",
        "function_code": "QUAN_LY_XE_CAI_TIEN",
        "action_code": "DANH_GIA_BAI_VIET"
    },
    # KIEM_SOAT
    "history_ptq": {
        "func" : "history-ptq",
        "function_code": "KIEM_SOAT",
        "action_code": "XEM_DANH_SACH_KIEM_SOAT"
    },
    "explanation": {
        "func" : "explanation",
        "function_code": "KIEM_SOAT",
        "action_code": "GIAI_TRINH_KIEM_SOAT"
    },
    "history_ptq_id": {
        "func" : "history-ptq-id",
        "function_code": "KIEM_SOAT",
        "action_code": "XEM_CHI_TIET_KIEM_SOAT"
    },
}
