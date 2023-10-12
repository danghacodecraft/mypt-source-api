from decouple import config

APP_ENV = config("APP_ENV")

status_checked = '<span style= "color:#a94442">Đã kiểm soát</span>'
status_warning = '<span style= "color:#a94442">Đang kiểm soát</span>'
status_uncontrollable = '<span style= "color:#a94442">Chưa kiểm soát</span>'
status_no_image = '<span style= "color:#a94442">Khong co ảnh</span>'
status_waiting_controlled = '<span style= "color:#a94442">Chờ kiểm soát lại</span>'

# Chat luong image origin; 200; 480
url_img = 'http://iqc.fpt.vn/img/Origin/'
url_img_200 = 'http://iqc.fpt.vn/img/200/'
url_img_480 = 'http://iqc.fpt.vn/img/480/'

host_iqc_prod = 'http://istorage.fpt.net'

IQC_BASE_URL_UPLOAD = "http://iqc.fpt.vn/api/"

IQC_CONFIG_CACHE_KEY_NAME = "iqcConfig"
# Ds key trong table mypt_iqc_configs can luu redis
IQC_CONFIG_RETURN_CONTRACT_CAUSE = "RETURN_CONTRACT_CAUSE"
IQC_CONFIG_PRACTICE_POINT_CAUSE = "PRACTICE_POINT_CAUSE"
IQC_CONFIG_TRANSACTION_TYPES = "TRANSACTION_TYPES"
IQC_CONFIG_HOUSE_MODELS = "HOUSE_MODELS"
IQC_CONFIG_TITLE_DEPLOYMENT_CONTRACT = "TITLE_DEPLOYMENT_CONTRACT"

LIST_DATA_IQC_CONFIG = [IQC_CONFIG_RETURN_CONTRACT_CAUSE, IQC_CONFIG_PRACTICE_POINT_CAUSE, IQC_CONFIG_TRANSACTION_TYPES,
                        IQC_CONFIG_HOUSE_MODELS]
LIST_DATA_IQC_CONFIG_CAPITALIZE = [IQC_CONFIG_TRANSACTION_TYPES, IQC_CONFIG_HOUSE_MODELS]

IMAGE_UPLOAD_DEADLINE = 24
MIN_RETURN_CONTRACT_IMAGE_UPLOAD = 1
MAX_RETURN_CONTRACT_IMAGE_UPLOAD = 10
FIXED_DEPLOYMENT_CONTRACT_IMAGE_UPLOAD = 6
MAX_PAGE_SIZE = 15

MIN_MAX_IMAGE_UPLOAD = {
    "trien_khai": {
        "MIN": 1,
        "MAX": 6
    },
    "ha_tang_ngoai_vi": {
        "MIN": 1,
        "MAX": 20
    },
    "hop_dong_tra_ve": {
        "MIN": 1,
        "MAX": 10
    },
}

PROXIES = {
    "http": None,
    "https": "proxy.hcm.fpt.vn",
}

if APP_ENV == "production":
    VIEW_IMAGE_AUTH_PUBLIC = "https://apis.fpt.vn/mypt-media-api/v1/view-image-iqc?path="
elif APP_ENV == "staging":
    VIEW_IMAGE_AUTH_PUBLIC = "https://apis-stag.fpt.vn/mypt-media-api/v1/view-image-iqc?path="
else:
    VIEW_IMAGE_AUTH_PUBLIC = "http://127.0.0.1:8002/mypt-media-api/v1/view-image-iqc?path="
