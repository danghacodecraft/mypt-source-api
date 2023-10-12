from decouple import config

APP_ENV = config("APP_ENV")

STATUS_CODE_ERROR_LOGIC = 4
STATUS_CODE_NO_DATA = 6
STATUS_CODE_SUCCESS = 1
STATUS_CODE_FAILED = 0

STATUS_CODE_INVALID_INPUT = 5
MESSAGE_API_SUCCESS = "Thành công"
MESSAGE_API_FAILED = "Thất bại"
MESSAGE_API_NO_DATA = "Không có thông tin"
MESSAGE_API_NO_INPUT = "Vui lòng nhập đầy đủ thông tin"
MESSAGE_API_SUCCESS_CHECKIN = "Điểm danh thành công"
MESSAGE_API_FAILED_CHECKIN = "Điểm danh không thành công"

MYSQL_ACCOUNT_MANAGEMENT_TB = 'account_management_tb'
MYSQL_EMP_CHECKIN_TB = 'emp_checkin_tb'
MYSQL_MYPT_CHECKIN_EMP_CHECKIN_HISTORY = 'mypt_checkin_emp_checkin_history'
MYSQL_MYPT_CHECKIN_EMP_RESPONSE = 'mypt_checkin_emp_response'
MYSQL_MYPT_RESPONSE_CONTENT = 'mypt_checkin_response_content'
MYSQL_MYPT_CHECKIN_SEND_EMAIL = 'mypt_checkin_send_email'

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_EXPORT = '%d/%m/%Y'
DATE_FORMAT_EXPORT_2 = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT2 = '%Y-%m-%d_%H-%M-%S'
DATETIME_FORMAT3 = '%Y%m%d_%H%M%S'
DATETIME_FORMAT_EXPORT = '%d/%m/%Y %H:%M:%S'

LIST_BLOCK_V1 = ['TIN01', 'TIN01', 'TIN03', 'TIN04', 'TIN05', 'TIN06', 'TIN07', 'TIN08', 'TIN08',
                 'TIN10', 'TIN11', 'TIN12', 'TIN13', 'TIN14', 'TTF01', 'TTF02', 'TTF03']

LIST_BLOCK_V2 = ['BGGTI', 'BNHTI', 'CBGTI', 'HYNTI', 'LCITI', 'LSNTI', 'PTOTI', 'QNHT1', 'QNHT2', 'TNNTI', 'TQGTI',
                 'VPCTI', 'YBITI']

LIST_BLOCK_V3 = ['DBNTI', 'HBHTI', 'HDGTI', 'HDGTI', 'HNMTI', 'HPGTI', 'HTHTI', 'NANTI', 'NBHTI', 'NDHTI', 'SLATI',
                 'TBHTI', 'THATI']

LIST_BLOCK_V4_TI = ['DNGTI', 'HUETI', 'QBHTI', 'QTITI']

# list_block = list_block_v5 + list_block_v4 + list_block_v6 + list_block_v7

LIST_BLOCK = LIST_BLOCK_V1 + LIST_BLOCK_V2 + LIST_BLOCK_V3 + LIST_BLOCK_V4_TI

if APP_ENV == "production":
    # http: // mypt - ho - profile - api - staging
    PRIVATE_NOTIFICATION_URL = "http://mypt-notification-api/"
    PRIVATE_HO_NOTIFICATION_URL = "http://mypt-ho-notification-api/"
    PRIVATE_SETTING_URL = "http://mypt-setting-api/"
else:
    # PRIVATE_NOTIFICATION_URL = "http://mypt-notification-api-staging/"
    PRIVATE_SETTING_URL = 'http://mypt-setting-api-staging/'
    PRIVATE_HO_NOTIFICATION_URL = "http://mypt-ho-notification-api/"
    PRIVATE_NOTIFICATION_URL = 'http://myptpdx-api-stag.fpt.net/'

NAME_SERVICE_NOTIFICATION = "mypt-notification-api/"
NAME_SERVICE_HO_NOTIFICATION = "mypt-ho-notification-api/"
NAME_SERVICE_SETTING = 'mypt-setting-api/'

# if APP_ENV == 'production':
#     URL = "http://myptpdx-api.fpt.net/"
# else:
#     URL = "http://myptpdx-api-stag.fpt.net/"
#
# NAME_SERVICE_PROFILE = "mypt-ho-profile-api/"


SERVICE_CONFIG = {
    "survey":{
        "base_http": "http://survey.fpt.vn/",
        "getDetailPointEmp": "api/v1/get-detail-point-emp",
        "method": "POST"
    },
    "hr":{
        "base_http": "http://hrapi.fpt.vn/api/",
        "auth": "TokenAuth/Authenticate",
        "method": "POST",
        "param": {
            "UserNameOrEmail": "pnc@hr.fpt.vn",
            "password": "!@#Pnc123",
            "rememberClient": "True"
        },
        "GetEmployeeInfo" : "services/app/pnc/GetEmployeeInfo",
        "GetCheckinReport" : "services/app/pnc/GetCheckinReport"
    }
}

DICT_DATA_TEXT_INFO = {
    "late": "Điểm danh trễ",
    "ontime": "Điểm danh đúng giờ",
    "notok" : "Chưa ghi nhận điểm danh"
}