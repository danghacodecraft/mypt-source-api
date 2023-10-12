import enum
 
NO_PROXY = {
    "http":"",
    "https":"",
}

HAVE_PROXY = {
    "http":"http://proxy.hcm.fpt.vn:80",
    "https":"http://proxy.hcm.fpt.vn:80",
}

HEADERS_DEFAULT = {
    "Content-Type": "application/json"
}

EXPIRE_TOOL_STATUS = 30

class STATUS_TOOLS(enum.Enum):
    ALL : str = "Tất cả"
    EXPIRED : str = "Hết hạn"
    ABOUT_TO_EXPIRED : str = "Sắp hết hạn"
    NO_EXPIRED : str = "Còn hạn"
    
class HOME_STATUS(enum.Enum):
    ALL : str = "Tổng số"
    ABOUT_TO_EXPIRED : str = "Sắp hết hạn"
    EXPIRED : str = "Hết hạn"
    
TAB_TOOLS_CONDITION = {
    "EXPIRED":[
        {
            "condition":"expire_date__lt",
            "number":0
        }
    ],
    "ABOUT_TO_EXPIRED":[
        {
            "condition":"expire_date__lt",
            "number":EXPIRE_TOOL_STATUS
        },
        {
            "condition":"expire_date__gt",
            "number":0
        }
    ],
    "NO_EXPIRED":[
        {
            "condition":"expire_date__gt",
            "number":0
        }
    ]
}

function_code = {
    "mypt-job-api/v1/show-tools":"CCDC",
    "mypt-job-api/v1/count-tools-expiration":"CCDC",
}

action_code = {
    "mypt-job-api/v1/show-tools":"XEM_DS_CCDC",
    "mypt-job-api/v1/count-tools-expiration":"SO_LUONG_CCDC",
}