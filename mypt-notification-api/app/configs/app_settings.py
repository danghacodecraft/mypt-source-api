AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

ROUTES_PREFIX = "mypt-notification-api/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "timeauthmiddleware": [
        "/" + ROUTES_PREFIX + "user-token"
    ],
    "authenusermiddleware": [        
        "/" + ROUTES_PREFIX + "send-noti",
        "/" + ROUTES_PREFIX + "get-notis-home",
        "/" + ROUTES_PREFIX + "do-tick",
        "/" + ROUTES_PREFIX + "do-bell",
        "/" + ROUTES_PREFIX + "do-action",               
        # "/" + ROUTES_PREFIX + "send-multi-noti-with-same-content-by-email",               
        # "/" + ROUTES_PREFIX + "send-multi-noti-with-diff-content-by-email",               
    ] 
}

OAUTH_CLIENT_ID = "My_PT"

EXPIRES_AT_ACCESS_TOKEN = 60
EXPIRES_AT_REFRESH_TOKEN = 43200
