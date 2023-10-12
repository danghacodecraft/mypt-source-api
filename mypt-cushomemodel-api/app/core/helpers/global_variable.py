from decouple import config

APP_ENV = config("APP_ENV")

FOLDER_PATH = "/opt/pdx/mypt"
UPLOAD_DIRECTORY = FOLDER_PATH + "/upload"

STATUS_CODE_ERROR_LOGIC = 6
STATUS_CODE_NO_DATA = 8
STATUS_CODE_SUCCESS = 1
STATUS_CODE_FAILED = 0
STATUS_CODE_ERROR_SYSTEM = 4
STATUS_CODE_INVALID_INPUT = 5

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_SUCCESS = "Thành công"
MESSAGE_API_ERROR_LOGIC = "Thất bại"
MESSAGE_API_NO_DATA = "Không có thông tin"
MESSAGE_API_NO_INPUT = "Vui lòng nhập đầy đủ thông tin"
MESSAGE_API_TIMEOUT = "Gateway Time-out"

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT4 = '%d/%m/%Y'
DATE_FORMAT_HIFPT = '%Y-%d-%m'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT_EXPORT_EXCEL = '%d/%m/%Y %H:%M:%S'
DATETIME_FORMAT2 = '%Y-%m-%d_%H-%M-%S'
DATETIME_FORMAT3 = '%Y%m%d_%H%M%S'

DATETIME_FORMAT_EXPORT = '%H:%M:%S %d/%m/%Y'
DATETIME_FORMAT_EXPORT_2 = '%H:%M %d/%m/%Y' # format ngay version 2
DATE_FORMAT_EXPORT = '%d/%m/%Y'

TXT_ERROR_MESSAGE_FORMAT = {
    'required': 'Thông tin {item} là bắt buộc',
    'invalid': 'Thông tin {item} không hợp lệ',
    'blank': 'Thông tin {item} không được để trống',
    'null': 'Vui lòng chọn/nhập thông tin {item}',
    'empty': 'Thông tin {item} không được rỗng',
    'invalid_image': 'Thông tin {item} không hợp lệ',
    'not_a_list': 'Thông tin {item} không hợp lệ',
}


FORMAT_DATETIME = {
    'datetime_vietnam': '%d/%m/%Y %H:%M:%S',
    'date_vietnam': '%d/%m/%Y',
    'datetime': '%Y-%m-%d %H:%M:%S',
    'date': '%Y-%m-%d',
    'time': '%H:%M:%S',
}
