from decouple import config

APP_ENV = config("APP_ENV")


RESPONSE_MESSAGES = {
    503: "unknown error",
    5: "Input invalid",
    110: "Nhập mật khẩu lương để xem chức năng này"
}
FORMAT_DATE_DEFAULT = "%d/%m/%Y"
FORMAT_DATETIME_DEFAULT = "%d/%m/%Y %H:%M:%S"

FORMAT_DATETIME_TZ = "%Y-%m-%dT%H:%M:%SZ"

if APP_ENV == "production":
    VIEW_FILE_AUTH_PUBLIC = "https://apis.fpt.vn/mypt-media-api/v1/view-file-auth?path="
else:
    VIEW_FILE_AUTH_PUBLIC = "https://apis-stag.fpt.vn/mypt-media-api/v1/view-file-auth?path="

LATEST_APP_VERSION_INFO = "LATEST_APP_VERSION_INFO"
