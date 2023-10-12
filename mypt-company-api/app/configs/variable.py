from decouple import config

ERROR = {
    "SERVER" : "Lỗi truy vấn",
    "REQUIRED_ID" : "Phải truyền id",
    "TOKEN_NO_INFO" : "Token không có thông tin",
    "NO_RIGHT_EDIT" : "Không có quyền sửa",
    "NO_RIGHT_DELETE" : "Không có quyền xoá",
    "NO_RIGHT_RATE" : "Không có quyền đánh giá",
    "NO_CHOOSE_ROW" : "Không có dòng nào được chọn",
    "BLOG_NOT_EXISTS" : "Bài viết không tồn tại hoặc đã xoá",
    "CREATE_RATE" : "Gửi đánh giá thất bại !",
    "RATE_EXISTS" : "Bạn chỉ được đánh giá 1 lần cho 1 bài viết.",
    "DATE_START" : "Ngày bắt đầu không được lớn hơn ngày kết thúc",
    "DATE_NOW" : "Ngày truyền lên không được lớn hơn ngày hiện tại",
    "PTQ_EXISTS":"Chế tài không tồn tại",
    "EXPLANATION":"Không được giải trình"
}

SUCCESS = {
    "ADD" : "Thêm mới thành công",
    "UPDATE" : "Cập nhật thành công",
    "CREATE_BLOG": "Cảm bạn đã chia sẻ",
    "CREATE_RATE": "Gửi đánh giá thành công !",
    "EXPLANATION":"Gửi giải trình thành công"
}

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_FORMAT_QUERY = "%Y-%m-%d"

APP_ENV = config("APP_ENV")

if APP_ENV == "production":
    # MEDIA_URL = "http://myptpdx-api.fpt.net/"
    MEDIA_URL = "http://mypt-ho-media-api/"
    PRIVATE_NOTIFICATION_URL = "http://mypt-notification-api/"
    # URL = "http://localhost:9999/"
else:
    MEDIA_URL = "http://mypt-ho-media-api-staging/"
    # MEDIA_URL = "http://127.0.0.1:8000/"
    PRIVATE_NOTIFICATION_URL = "http://mypt-notification-api-staging/"
    # MEDIA_URL = "http://myptpdx-api-stag.fpt.net/"
    # URL = "http://localhost:9999/"

NAME_SERVICE_MEDIA = "mypt-ho-media-api/"

STATUS_CODE_ERROR_LOGIC = 4
STATUS_CODE_NO_DATA = 6
STATUS_CODE_SUCCESS = 1
STATUS_CODE_INVALID_INPUT = 5
STATUS_CODE_FAILED = 0
STATUS_CODE_ERROR_SYSTEM = 4

MESSAGE_API_SUCCESS = "Thành công"
MESSAGE_API_FAILED = "Thất bại"
MESSAGE_API_NO_DATA = "Không có thông tin"
MESSAGE_API_NO_INPUT = "Vui lòng nhập đầy đủ thông tin"

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_ERROR_LOGIC = "Thất bại"

ROLE_CODE_NHAN_VIEN_DANH_GIA = 'NHAN_VIEN_DANH_GIA'
ROLE_CODE_NHAN_VIEN_DANH_GIA_TIN = 'NHAN_VIEN_DANH_GIA_TIN'
ROLE_CODE_NHAN_VIEN_DANH_GIA_PNC = 'NHAN_VIEN_DANH_GIA_PNC'

THROTTLING = {
        'rate': '1',
        'split': '/',
        'per_time': '1s',
        'method': [
            'GET'
        ],
}

DEFAULT_AVATAR = "https://apis.fpt.vn/mypt-ho-media-api/download-file?path=0098940307294320"
