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

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_EXPORT = '%d/%m/%Y'
DATE_FORMAT_EXPORT_2 = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT2 = '%Y-%m-%d_%H-%M-%S'
DATETIME_FORMAT3 = '%Y%m%d_%H%M%S'
DATETIME_FORMAT_EXPORT = '%d/%m/%Y %H:%M:%S'
