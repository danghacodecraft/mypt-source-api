EMPLOYEE_POSITION = {
    "CB Hỗ trợ kỹ thuật từ xa": {
        "is_show_block": False,
        "is_show_salary": False,
        "is_show_occupational_safety_card": False,
        "is_show_job_level": True
    },
    "CB Kỹ thuật FTTH": {
        "is_show_block": True,
        "is_show_salary": False,
        "is_show_occupational_safety_card": True,
        "is_show_job_level": True

    },
    "CB Hỗ trợ kỹ thuật tại nhà KH": {
        "is_show_block": True,
        "is_show_salary": True,
        "is_show_occupational_safety_card": True,
        "is_show_job_level": True
    },
    "CB Kỹ thuật TKBT": {
        "is_show_block": True,
        "is_show_salary": True,
        "is_show_occupational_safety_card": True,
        "is_show_job_level": True
    },
    "CB Xử lý sự cố": {
        "is_show_block": False,
        "is_show_salary": False,
        "is_show_occupational_safety_card": False,
        "is_show_job_level": True

    },
}

CONTRACT_TYPE = {
    "new": [
        "hợp đồng đào tạo nghề",
        "hợp đồng thử việc",
        "hđ đào tạo nghề",
        "hđ thử việc",
        "thử việc"
    ],
    'office': [

    ]
}

AVATAR = {
    "type": "_1.jpg",
    "host": "https://mytinpnc.vn/data/avatar_img/"
}

SAFE_CARD_LINK = {
    "host": "https://mytinpnc.vn/imgs/"
}

# SAFE_CARD_DOMAIN = {
#     "local": "http://127.0.0.1:8003/",
#     "dev": "",
#     "staging": "https://apis-stag.fpt.vn/",
#     "production": "https://apis.fpt.vn/"
# }

AVATAR_DEFAULT = {
    "male": "https://apis.fpt.vn/mypt-ho-media-api/download-file?path=0098940307294320",
    "female": "https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0269357356197571"
}

PROXIES = {
    "http": "http://proxy.hcm.fpt.vn:80",
    "https": "http://proxy.hcm.fpt.vn:80"
}

SCREEN = {
    "default":0,
    "TPL":1
}
CONFIGS_KEY = {
    "TPL":{
        "QL đội triển khai bảo trì",
        "QL Kỹ thuật hệ thống mạng",
        "CB Kinh doanh dự án",
        "QL Quản lý đối tác",
        "Đội trưởng TKBT"
    }
}

# service company
ROLE_CODE_NHAN_VIEN_DANH_GIA = 'NHAN_VIEN_DANH_GIA'
ROLE_CODE_NHAN_VIEN_DANH_GIA_PNC = 'NHAN_VIEN_DANH_GIA_PNC'
ROLE_CODE_NHAN_VIEN_DANH_GIA_TIN = 'NHAN_VIEN_DANH_GIA_TIN'


#status code
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
