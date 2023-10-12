from django.conf import settings
from http.models.user_permission import UserPermission

def fill_user_permission(user_id: int, user_info: dict, curr_permission: list):
    try:
        LIST_PARENT_DEPART_TICKET_RIGHT = ["PNCV4", "PNCV5", "PNCV6", "PNCV7", "TINV1", "TINV2", "TINV3", "TINV4"]
        LIST_JOB_TITLE_TICKET_RIGHT = ['cb hỗ trợ kỹ thuật từ xa', 'cb hỗ trợ kỹ thuật tại nhà kh', "cb xử lý sự cố"]
        LIST_JOB_TITLE_CHECKIN_RIGHT = ['cb kỹ thuật tkbt', 'cb hỗ trợ kỹ thuật từ xa', 'cb hỗ trợ kỹ thuật tại nhà kh','cb xử lý sự cố']
        LIST_CONTRACT_CHECKIN_RIGHT = ['hợp đồng đào tạo nghề', 'hợp đồng thử việc', "hđ đào tạo nghề", "hđ thử việc"]
        LIST_JOB_TITLE_SALARY_RIGHT = ["cb kỹ thuật tkbt", "cb hỗ trợ kỹ thuật tại nhà kh"]
        LIST_JOB_TITLE_KPIS_RIGHT = ["cb kỹ thuật tkbt", "cb hỗ trợ kỹ thuật tại nhà kh", "cb hỗ trợ kỹ thuật từ xa"]
        LIST_JOB_TITLE_IQC_RIGHT = ["cb kỹ thuật tkbt", "cb xử lý sự cố"]

        allow_technical_support_permissions = user_info["jobTitle"].lower() in LIST_JOB_TITLE_TICKET_RIGHT or user_info["childDepart"] == "PHTTX" or user_info["parentDepart"] in LIST_PARENT_DEPART_TICKET_RIGHT
        allow_check_in_permissions = user_info["jobTitle"].lower() in LIST_JOB_TITLE_CHECKIN_RIGHT or user_info["contractType"].lower() in LIST_CONTRACT_CHECKIN_RIGHT
        allow_salary_permissions = user_info["jobTitle"].lower() in LIST_JOB_TITLE_SALARY_RIGHT
        allow_kpi_permissions = user_info["jobTitle"].lower() in LIST_JOB_TITLE_KPIS_RIGHT
        allow_iqc_permissions = user_info["jobTitle"].lower() in LIST_JOB_TITLE_IQC_RIGHT
        
        ALL_PERMISSION = {
            "TECHNICAL_SUPPORT": {
                "XEM_TICKET_HTKT_CUA_TOI": {
                    "user_id": user_id,
                    "permission_id": 4,
                    "permission_code":  "XEM_TICKET_HTKT_CUA_TOI",
                    "child_depart": ""
                }, 
                "TAO_TICKET_HTKT": {
                    "user_id": user_id,
                    "permission_id": 9,
                    "permission_code":  "TAO_TICKET_HTKT",
                    "child_depart": ""
                },
                "DANH_GIA_TICKET_HTKT": {
                    "user_id": user_id,
                    "permission_id": 10,
                    "permission_code":  "DANH_GIA_TICKET_HTKT",
                    "child_depart": ""
                }
            },
            "CHECK_IN": {
                "THUC_HIEN_DIEM_DANH": {
                    "user_id": user_id,
                    "permission_id": 2,
                    "permission_code":  "THUC_HIEN_DIEM_DANH",
                    "child_depart": ""
                }, 
                "XEM_LICH_SU_DIEM_DANH": {
                    "user_id": user_id,
                    "permission_id": 3,
                    "permission_code":  "XEM_LICH_SU_DIEM_DANH",
                    "child_depart": ""
                }
            },
            "SALARY": {
                "XEM_LUONG": {
                    "user_id": user_id,
                    "permission_id": 11,
                    "permission_code":  "XEM_LUONG",
                    "child_depart": ""
                }
            },
            "KPI": {
                "XEM_KQCV_KPIS": {
                    "user_id": user_id,
                    "permission_id": 13 if settings.APP_ENVIRONMENT in ["production", "local"] else 12,
                    "permission_code":  "XEM_KQCV_KPIS",
                    "child_depart": ""
                }
            },
            "IQC": {
                "USE_IQC": {
                    "user_id": user_id,
                    "permission_id": 17 if settings.APP_ENVIRONMENT in ["production", "local"] else 14,
                    "permission_code": "USE_IQC",
                    "child_depart": ""
                }
            }
        }

        new_permissions = []
        curr_permission_codes = curr_permission.keys()
        
        if allow_technical_support_permissions:
            for permission in [*ALL_PERMISSION["TECHNICAL_SUPPORT"]]:
                if permission not in curr_permission_codes:
                    new_permissions.append(ALL_PERMISSION['TECHNICAL_SUPPORT'][permission])
                    
        if allow_check_in_permissions:
            for permission in [*ALL_PERMISSION["CHECK_IN"]]:
                if permission not in curr_permission_codes:
                    new_permissions.append(ALL_PERMISSION['CHECK_IN'][permission])
                    
        if allow_salary_permissions:
            for permission in [*ALL_PERMISSION["SALARY"]]:
                if permission not in curr_permission_codes:
                    new_permissions.append(ALL_PERMISSION['SALARY'][permission])
                    
        if allow_kpi_permissions:
            for permission in [*ALL_PERMISSION["KPI"]]:
                if permission not in curr_permission_codes:
                    new_permissions.append(ALL_PERMISSION['KPI'][permission])

        if allow_iqc_permissions:
            for permission in [*ALL_PERMISSION["IQC"]]:
                if permission not in curr_permission_codes:
                    new_permissions.append(ALL_PERMISSION['IQC'][permission])

        # return False
        if new_permissions:
            fill_permissions = UserPermission.objects.bulk_create(
                list(map(lambda permission : UserPermission(**permission), new_permissions))
            )
            return True
        return False
    except Exception as e:
        print("==>", e)
        return False
    