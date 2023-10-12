SERVICE_CONFIG = {
    'HO_PROFILE': {
        'local': 'http://127.0.0.1:8002/mypt-ho-profile-api/',
        'staging': 'http://mypt-ho-profile-api-staging/mypt-ho-profile-api/',
        'production': 'http://mypt-ho-profile-api/mypt-ho-profile-api/',
        'update_employees_info_with_permissions_and_fea_roles': {
            'func': 'update-employees-info-with-permissions-and-fea-roles',
            'method': 'POST'
        },
        'check_email_has_fea_roles_by_codes': {
            'func': 'check-email-has-fea-roles-by-codes',
            'method': 'POST'
        }
    },
    'HO_CHM': {
        'local': 'http://127.0.0.1:8201/mypt-ho-cushomemodel-api/',
        'staging': 'http://mypt-ho-cushomemodel-api-staging/mypt-ho-cushomemodel-api/',
        'production': 'http://mypt-ho-cushomemodel-api/mypt-ho-cushomemodel-api/',
        'save_log_api': {
            'func': 'save-log-api',
            'method': 'POST'
        }
    },
    'HO_MEDIA': {
        'local': 'http://127.0.0.1:8006/mypt-ho-media-api/',
        'staging': 'http://mypt-ho-media-api-staging/mypt-ho-media-api/',
        'production': 'http://mypt-ho-media-api/mypt-ho-media-api/',
        'upload_file_private': {
            'func': 'upload-file-private',
            'method': 'POST'
        },
        'view_file': {
            'func': 'view-file',
            'method': 'GET'
        }
    }
}

AI_MODEL_2D = {
    'MODEL_2D': {
        'local': {
            'url': 'http://housemodel-api.mypt.vn/wifi-simulation-api/',
            'env': 'production'
        },
        'staging': {
            'url': 'http://housemodel-api.mypt.vn/wifi-simulation-api/',
            'env': 'production'
        },
        'production': {
            'url': 'http://housemodel-api.mypt.vn/wifi-simulation-api/',
            'env': 'production'
        },
        'transform_image': {
            'func': 'transform-image',
            'method': 'POST'
        },
        'simulate_wifi': {
            'func': 'simulate-wifi',
            'method': 'POST'
        },
        'ap_suggestion': {
            'func': 'ap-suggestion',
            'method': 'POST'
        },
        'transform_image_app': {
            'func': 'transform-image-app',
            'method': 'POST'
        },
        'simulate_wifi_app': {
            'func': 'simulate-wifi-app',
            'method': 'POST'
        },
        'ap_suggestion_app': {
            'func': 'ap-suggestion-app',
            'method': 'POST'
        }
    }
}

INSIDE_CONFIG = {
    # 2 api này dùng để gọi danh sách hiện trạng hợp đồng từ inside
    'CONTRACT_INFO_EQUIPMENT': {
        'local': 'https://sapi.fpt.vn/',
        'staging': 'https://sapi.fpt.vn/',
        'production': 'https://sapi.fpt.vn/',
        'generate_token': {
            'func': 'token/GenerateToken',
            'method': 'GET'
        },
        'get_info_by_contract_TIN_PNC': {
            'func': 'systemapi/api/ContractApi/GetInfoByContractTINPNC',
            'method': 'GET'
        }
    },
    # 3 api dưới dùng để gọi lấy danh sách thiết bị AP/Modem từ inside
    'LIST_EQUIPMENTS_INFO': {
        'local': 'http://inside-api.fpt.net/par-transition/',
        'staging': 'http://inside-api-stag.fpt.net/par-transition/',
        'production': 'http://inside-api.fpt.net/par-transition/',
        'authenticate': {
            'func': 'identity/api/v1/Authenticate',
            'method': 'POST'
        },
        'authenticate_refresh_token': {
            'func': 'identity/api/v1/Authenticate/refresh-token',
            'method': 'POST'
        },
        'get_list_equipment_info': {
            'func': 'equipment/api/v1/EquipmentHome/GetMobiQCSendEquipmentInfo',
            'method': 'GET'
        }
    }
}
