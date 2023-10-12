SERVICE_CONFIG = {
    "NOTIFICATION": {
        "base_http_local": "http://myptpdx-api-stag.fpt.net/mypt-notification-api/",
        "base_http_staging": "http://mypt-ho-notification-api-staging/mypt-notification-api/",
        "base_http_production": "http://mypt-ho-notification-api/mypt-notification-api/",
        "send_noti": {
            "func": "send-one-noti",
            "method": "POST"
        }
    },
    "SETTING": {
        "base_http_local": "http://mypt.local/mypt-setting-api/v1/",
        "base_http_staging": "http://mypt-setting-api-staging/mypt-setting-api/v1/",
        "base_http_production": "http://mypt-setting-api/mypt-setting-api/v1/",
        "show_hide_tab": {
            "func": "show-hide-user-home-tab",
            "method": "POST"
        }
    },
    "HO-CHECKIN": {
        "base_http_local": "http://localhost:8003/mypt-ho-checkin-api/",
        "base_http_staging": "http://myptpdx-api-stag.fpt.net/mypt-ho-checkin-api/",
        "base_http_production": "http://myptpdx-api.fpt.net/mypt-ho-checkin-api/",
        "save_mbn_account_from_isc": {
            "func": "save-all-account-mobi-to-redis",
            "method": "POST"
        }
    },
    "IQC": {
        "base_http_local": "http://mypt.local:8000/mypt-iqc-api/v1/",
        "base_http_staging": "http://myptpdx-api-stag.fpt.net/mypt-iqc-api/v1/",
        "base_http_production": "http://myptpdx-api.fpt.net/mypt-iqc-api/v1/",
        "get_list_house_model": {
            "func": "get-list-house-model",
            "method": "GET"
        },
        "get_list_transaction_type": {
            "func": "get-list-transaction-type",
            "method": "GET"
        },
        "get_list_return_contract_cause": {
            "func": "get-list-return-contract-cause",
            "method": "GET"
        },
        "practice_point_get_cause_image": {
            "func": "practice-point-get-cause-image",
            "method": "GET"
        },
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

IQC_API = {
    "base_http_local": "http://istorage-stag.fpt.net/",
    "base_http_staging": "http://istorage-stag.fpt.net/",
    "base_http_production": "http://istorage.fpt.net/",
    "load_iqc_upload_return_contract": {
        "func": "api/contract/list",
        "method": "GET"
    },
    "load_iqc_detail_return_contract": {
        "func": "api/contract/contractDetail",
        "method": "GET"
    },
    "create_return_contract": {
        "func": "api/contract/image",
        "method": "POST"
    },
    "update_return_contract": {
        "func": "api/contract/image",
        "method": "PUT"
    },
    "load_album_deployment": {
        "func": "api/iqc/album",
        "method": "GET"
    },
    "get_contract_deployment_detail": {
        "func": "api/iqc/contractDetail",
        "method": "GET"
    },
    "create_contract_deployment": {
        "func": "api/iqc/createImage",
        "method": "POST"
    },
    "update_contract_deployment": {
        "func": "api/iqc/updateImage",
        "method": "POST"
    },
    "load_iqc_upload_practice_point": {
        "func": "api/practicePoint/album",
        "method": "GET"
    },
    "load_iqc_detail_practice_point": {
        "func": "api/practicePoint/detail",
        "method": "GET"
    },
    "create_practice_point": {
        "func": "api/practicePoint/create",
        "method": "POST"
    },
    "update_practice_point": {
        "func": "api/practicePoint/update",
        "method": "POST"
    },
    "practice_point_get_cause_image": {
        "func": "api/practicePoint/getCauseImage",
        "method": "GET"
    },
    "get_practice_point_check_version": {
        "func": "api/practicePoint/checkVersion",
        "method": "GET"
    },
    "get_practice_point_search": {
        "func": "api/practicePoint/search",
        "method": "POST"
    },
    "search_deployment_contract": {
        "func": "api/iqc/search",
        "method": "GET"
    },
    "search_practice_point": {
        "func": "api/practicePoint/search",
        "method": "GET"
    },
    "search_return_contract": {
        "func": "api/contract/search",
        "method": "GET"
    }
}

SERVICE_CONFIG_SAVE_LOGS_API = {
    "service_name": "/mypt-iqc-api/v1/",
    # IQC
    "load_iqc_album_upload_deployment": {
        "func" : "load-iqc-album-upload-deployment",
        "function_code": "IQC",
        "action_code": "XEM_DANH_SACH_TRIEN_KHAI"
    },
    "get_iqc_detail_deployment": {
        "func" : "get-iqc-detail-deployment",
        "function_code": "IQC",
        "action_code": "XEM_CHI_TIET_TRIEN_KHAI"
    },
    "load_iqc_upload_practice_point": {
        "func" : "load-iqc-upload-practice-point",
        "function_code": "IQC",
        "action_code": "XEM_DANH_SACH_HA_TANG_NGOAI_VI"
    },
    "load_iqc_detail_practice_point": {
        "func" : "load-iqc-detail-practice-point",
        "function_code": "IQC",
        "action_code": "XEM_CHI_TIET_HA_TANG_NGOAI_VI"
    },
    "load_iqc_upload_return_contract": {
        "func" : "load-iqc-upload-return-contract",
        "function_code": "IQC",
        "action_code": "XEM_DANH_SACH_HD_TRA_VE"
    },
    "load_iqc_detail_return_contract": {
        "func" : "load-iqc-detail-return-contract",
        "function_code": "IQC",
        "action_code": "XEM_CHI_TIET_HD_TRA_VE"
    },
    "create_contract_deployment": {
        "func" : "create-contract-deployment",
        "function_code": "IQC",
        "action_code": "UPLOAD_TRIEN_KHAI"
    },
    "create_practice_point": {
        "func" : "create-practice-point",
        "function_code": "IQC",
        "action_code": "UPLOAD_HA_TANG_NGOAI_VI"
    },
    "create_or_update_return_contract": {
        "func" : "create-or-update-return-contract",
        "function_code": "IQC",
        "action_code": [
            "UPLOAD_HD_TRA_VE",
            "UPDATE_HD_TRA_VE"
        ]
    },
    "update_contract_deployment": {
        "func" : "update-contract-deployment",
        "function_code": "IQC",
        "action_code": "UPDATE_TRIEN_KHAI"
    },
    "update_practice_point": {
        "func" : "update-practice-point",
        "function_code": "IQC",
        "action_code": "UPDATE_HA_TANG_NGOAI_VI"
    },
}
