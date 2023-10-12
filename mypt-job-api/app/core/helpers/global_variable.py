from decouple import config

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
MESSAGE_API_INVALID_INPUT = "Nhâp sai thông tin"
MESSAGE_API_INVALID_FORMAT = "Nhập sai định dạng"

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_ERROR_LOGIC = "Thất bại"

APP_ENV = config("APP_ENV")
if APP_ENV == "production":
    MEDIA_URL = "http://mypt-ho-media-api/"
else:
    MEDIA_URL = "http://mypt-ho-media-api-staging/"
    # MEDIA_URL = "http://127.0.0.1:8000/"

NAME_SERVICE_MEDIA = "mypt-ho-media-api/"

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_ERROR_LOGIC = "Thất bại"

FORMAT_DATETIME_TZ = "%Y-%m-%dT%H:%M:%SZ"
FORMAT_DATE_DEFAULT = "%d/%m/%Y"
FORMAT_DATETIME_DEFAULT = "%d/%m/%Y %H:%M:%S"

DATETIME_FORMATED = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M', '%m/%d'
                                                                                                               '/%Y',
                     '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M', '%m/%d/%y']
DATETIME_Y_m_d = ['%Y-%m-%d %H:%M:%S']
YEAR_month_day = ['%Y-%m-%d']
day_month_YEAR = ['%d/%m/%Y']
month_YEAR = ['%m/%Y']

css_font_bold = "style='font-weight:600;'"
start_tag_b_html = "<b " + css_font_bold + ">"
end_tag_b_html = "</b>"
start_tag_div_html = "<div style='color:#8E98A4'>"
end_tag_div_html = "</div>"

text_fail_salary = start_tag_div_html + start_tag_b_html + "Không có dữ liệu" + end_tag_b_html + "<br>" + \
                   "Không có thông tin lương phù hợp. Bạn vui lòng liên hệ phòng HR để được hỗ trợ" + end_tag_div_html

text_pending_salaray = start_tag_div_html + "Chức năng xem lương tạm tính và lương công thức đang tạm ngừng hiển thị " \
                                            "để cập nhật nội dung mới." + "<br>" + \
                       "Phòng Nhân sự sẽ gửi chi tiết lương qua email của Anh/Chị kể từ kỳ lương Tháng 03.2023 và " \
                       "thông báo thời gian hoạt động trở lại của chức năng trên khi cập nhật xong." + "<br>" + \
                       "Anh/Chị vẫn có thể xem lại lịch sử lương hạch toán. Xin cảm ơn." + end_tag_div_html


RESPONSE_MESSAGES = {
    503: "unknown error",
    5: "Input invalid",
    110: "Nhập mật khẩu lương để xem chức năng này"
}

SALARY_CONTRACT_MAIL = {
    "PNC": "Hr1.pnc@fpt.net",
    "TIN": "Salary@vienthongtin.com"
}

SALARY_PASSWORD_OTP_TIMEOUT = 5
SALARY_PASSWORD_TIMEOUT = 60
SALARY_PASSWORD_NEW_SESSION_TIMEOUT = 15
SALARY_HOME_CACHE_KEY_NAME = 'salary:home'
SALARY_DAILY_CACHE_KEY_NAME = 'salary:daily'
SALARY_DAILY_OVERVIEW_CACHE_KEY_NAME = 'salary:daily_overview'
SALARY_MONTHLY_CACHE_KEY_NAME = 'salary:monthly'
SALARY_CONFIG_CACHE_KEY_NAME = 'salary:config'
SALARY_CACHE_DEFAULT_TIMEOUT = 30
SALARY_DAY_IMPORT_MONTHLY = 8
SALARY_END_DAY_IMPORT_MONTHLY = 15
SALARY_HOUR_SYNC_DAILY = 6  # Trừ hao 1 giờ
SALARY_MAX_LEVEL_EMPTY_VALUE = 1

INSIDE_API_DOMAIN_LOCAL = "http://inside-api-dev.fpt.net"
INSIDE_API_DOMAIN_STAGING = "http://inside-api-stag.fpt.net"
INSIDE_API_DOMAIN_PRODUCTION = "http://inside-api.fpt.net"
INSIDE_API_DOMAIN_BASE_URL = "http://inside-api.fpt.net/par-transition/"
INSIDE_API_CACHE_KEY_NAME = 'inside_api'
INSIDE_API_SALARY_CACHE_TIMEOUT = 15

SALARY_JOB_TITLE = [
    "CB Kỹ thuật TKBT",
    "cb kỹ thuật tkbt"
]

NONE_SALARY_FORMULA_MONTHLY = [
    {
        "index": "1",
        "id": "BasicSalary",
        "title": "Lương bậc nghề",
        "number": "0",
        "info": "",
        "details": []
    },
    {
        "index": "2",
        "id": "ProductivitySalary",
        "title": "Lương sản phẩm",
        "number": "0",
        "info": "",
        "details": []
    },
    {
        "index": "3",
        "id": "SumQuantitySalary",
        "title": "Lương chất lượng",
        "number": "0",
        "info": "",
        "details": []
    },
    {
        "index": "4",
        "id": "Punishment",
        "title": "Chế tài",
        "number": "0",
        "info": "",
        "details": []
    },
    {
        "index": "5",
        "id": "SumProductivitySalaryOther",
        "title": "Lương sản phẩm khác",
        "number": "0",
        "info": "",
        "details": [
            {
                "index": "5.1",
                "id": "TestSalary",
                "title": "Kiểm tra thiết bị",
                "number": "0",
                "info": "",
                "details": [
                    {
                        "index": "5.1.1",
                        "id": "TestQuantity",
                        "title": "Số lượng thiết bị test thành công",
                        "number": "0",
                        "info": "",
                        "details": []
                    }
                ]
            },
            {
                "index": "5.2",
                "id": "NoneProductivitySalary",
                "title": "Lương ngày công không phát sinh NSLĐ",
                "number": "0",
                "info": "",
                "details": [
                    {
                        "index": "5.2.1",
                        "id": "TimeNoneProductivity",
                        "title": "Số giờ không phát sinh NSLĐ",
                        "number": "0",
                        "info": "",
                        "details": []
                    }
                ]
            },
            {
                "index": "5.3",
                "id": "ServiceRestore",
                "title": "Khôi phục dịch vụ",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "5.4",
                "id": "RoseSale",
                "title": "Hoa hồng bán hàng",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "5.5",
                "id": "CollectSalary",
                "title": "Lương thu cước không chuyên",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "5.6",
                "id": "TravelSalary",
                "title": "Lương đồn trú",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "5.7",
                "id": "HDTT",
                "title": "Lương HĐ thu tiền đơn giá 10K",
                "number": "0",
                "info": "",
                "details": []
            }
        ]
    },
    {
        "index": "6",
        "id": "BasicSalary",
        "title": "Thu chi khác",
        "number": "0",
        "info": "",
        "details": [
            {
                "index": "6.1",
                "id": "AdditionalBefore",
                "title": "Bù trừ lương tháng T-1",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "6.2",
                "id": "RewardProductivity",
                "title": "Khen thưởng",
                "number": "0",
                "info": "",
                "details": [
                    {
                        "index": "6.2.1",
                        "id": "BonusFTEL",
                        "title": "Chương trình thi đua FTEL",
                        "number": "0",
                        "info": "",
                        "details": []
                    },
                    {
                        "index": "6.2.2",
                        "id": "BonusTINPNC",
                        "title": "Chương trình thi đua TINPNC",
                        "number": "0",
                        "info": "",
                        "details": []
                    }
                ]
            },
            {
                "index": "6.3",
                "id": "OtherAmount",
                "title": "Các khoản khác",
                "number": "0",
                "info": "",
                "details": [
                    {
                        "index": "6.3.1",
                        "id": "AddOtherFTEL",
                        "title": "Các khoản khác (FTEL)",
                        "number": "0",
                        "info": "",
                        "details": []
                    },
                    {
                        "index": "6.3.2",
                        "id": "AddOtherINPNC",
                        "title": "Các khoản khác (TINPNC)",
                        "number": "0",
                        "info": "",
                        "details": []
                    }
                ]
            }
        ]
    }
]

NONE_SALARY_REAL_MONTHLY = [
    {
        "index": "1",
        "id": "luong_thang",
        "title": "Lương tháng",
        "number": "0",
        "info": "",
        "details": [
            {
                "index": "1.1",
                "id": "luong_thu_viec",
                "title": "Lương thử việc/tập nghề",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "1.2",
                "id": "luong_cong_thuc",
                "title": "Lương công thức",
                "number": "0",
                "info": "",
                "details": []
            }
        ]
    },
    {
        "index": "2",
        "id": "luong_dong_bhxh",
        "title": "Lương đóng BHXH",
        "number": "0",
        "info": "",
        "details": [
            {
                "index": "2.1",
                "id": "bhyt",
                "title": "BHYT",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "2.2",
                "id": "bhxh",
                "title": "BHXH",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "2.3",
                "id": "bhtn",
                "title": "BHTN",
                "number": "0",
                "info": "",
                "details": []
            }
        ]
    },
    {
        "index": "3",
        "id": "kinh_phi_cd",
        "title": "Kinh phí công đoàn",
        "number": "0",
        "info": "",
        "details": []
    },
    {
        "index": "4",
        "id": "giam_tru_gia_canh",
        "title": "Giảm trừ gia cảnh",
        "number": "0",
        "info": "",
        "details": [
            {
                "index": "4.1",
                "id": "sl_nguoi_phu_thuoc",
                "title": "SL người phụ thuộc",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "4.2",
                "id": "muc_giam_tru_npt",
                "title": "Mức giảm trừ NPT",
                "number": "0",
                "info": "",
                "details": []
            }
        ]
    },
    {
        "index": "5",
        "id": "thue_thu_nhap_ca_nhan",
        "title": "Thuế TNCN",
        "number": "0",
        "info": "",
        "details": []
    },
    {
        "index": "6",
        "id": "bu_tru_khac_sau_thue",
        "title": "Bù trừ khác sau thuế",
        "number": "0",
        "info": "",
        "details": [
            {
                "index": "6.1",
                "id": "truy_thu_hoan_thue_tncn",
                "title": "Truy thu/hoàn thuế TNCN",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "6.2",
                "id": "truy_thu_bhyt",
                "title": "Truy thu BHYT",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "6.3",
                "id": "tam_ung",
                "title": "Tạm ứng",
                "number": "0",
                "info": "",
                "details": []
            },
            {
                "index": "6.4",
                "id": "hoan_ung",
                "title": "Hoàn ứng",
                "number": "0",
                "info": "",
                "details": []
            }
        ]
    }
]