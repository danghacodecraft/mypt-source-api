from decouple import config

APP_ENV = config("APP_ENV")

FOLDER_PATH = "/opt/pdx/mypt"
UPLOAD_DIRECTORY = FOLDER_PATH + "/upload"
CHILD_FOLDER_IN_LIBRARY = ["Quy định", "Quy trình", "Tài liệu hướng dẫn", "Chính sách", "Biên bản cuộc họp"]

if APP_ENV == "production":
    # UPLOAD_DIRECTORY_PUBLIC = "https://fpt.vn/mypt/imgs"
    UPLOAD_DIRECTORY_PUBLIC = "https://apis.fpt.vn/mypt-media-api/v1/view-file?path="
    DOWNLOAD_DIRECTORY_PUBLIC = "https://apis.fpt.vn/mypt-media-api/v1/download-file?path="

else:
    # UPLOAD_DIRECTORY_PUBLIC = "https://staging.fpt.vn/mypt/imgs"
    UPLOAD_DIRECTORY_PUBLIC = "https://apis-stag.fpt.vn/mypt-media-api/v1/view-file?path="
    DOWNLOAD_DIRECTORY_PUBLIC = "https://apis-stag.fpt.vn/mypt-media-api/v1/download-file?path="

STATUS_CODE_ERROR_LOGIC = 4
STATUS_CODE_NO_DATA = 6
STATUS_CODE_SUCCESS = 1
STATUS_CODE_FAILED = 0

STATUS_CODE_INVALID_INPUT = 5
MESSAGE_API_SUCCESS = "Thành công"
MESSAGE_API_FAILED = "Thất bại"
MESSAGE_API_NO_DATA = "Không có thông tin"
MESSAGE_API_NO_INPUT = "Vui lòng nhập đầy đủ thông tin"

SENDER = "pnc.pdx@fpt.net"

MYSQL_THU_VIEN_TB = 'thu_vien_tb'
MYSQL_MEETING_DETAIL_TB = 'meeting_detail_tb'
MYSQL_STORAGE_UUID_DATA_TB = 'storage_uuid_data_tb'
MYSQL_MYPT_MEDIA_LIST_FOLDER = 'mypt_media_list_folder'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT3 = '%Y%m%d_%H%M%S'
DATETIME_FORMAT5 = '%Y%m%d%H%M%S'
DATETIME_FORMAT_EXPORT = '%d/%m/%Y %H:%M:%S'

MESSAGE_UPLOAD_TYPE = {
    "DEFAULT": {
        "success_message": "Thành công",
        "error_messages": {
            "failed": "Thất bại",
            "file_size": "Kích thước file quá lớn",
            "file_type": "Loại file ko phù hợp",
            "tail_file": "Đuôi file không phù hợp",
            "tail_file_blank": "Không có đuôi file"
        }
    },
    "AVATAR": {
        "success_message": "Thay đổi ảnh đại diện thành công",
        "error_messages": {
            "failed": "Thay đổi ảnh đại diện không thành công",
            "file_size": "Ảnh vượt quá dung lượng tối đa.",
            "file_type": "Định dạng không hỗ trợ.",
            "tail_file": "Định dạng không hỗ trợ.",
            "tail_file_blank": "Không có đuôi file"
        }
    }
}
