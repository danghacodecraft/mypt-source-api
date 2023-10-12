AES_SECRET_KEY = "kds592jcw016brkq"

JWT_SECRET_KEY = "ov37kpFWsz81ks5dPmXgjU"

SERVICE_NAME = "mypt-cushomemodel-auth-api"

ROUTES_PREFIX = SERVICE_NAME + "/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "appuserandsessiontokenmiddleware": [
        "/" + ROUTES_PREFIX + "auth-user-token"
    ],
    "authenusermiddleware": [
        # "/" + ROUTES_PREFIX + "create-ticket",
    ],
    "userpermissionmiddleware": [
        # "/" + ROUTES_PREFIX + "create-ticket",
    ]
}

APP_KEY_MIDDLEWARE = []

LOCAL_AVAILABLE_TOKEN_SECONDS = 15
STAGING_AVAILABLE_TOKEN_SECONDS = 10
PRODUCTION_AVAILABLE_TOKEN_SECONDS = 10

ACC_CREDENTIALS_GRANT_ID = 1
REFRESH_TOKEN_GRANT_ID = 2

OAUTH_CLIENT_ID = "CHM_SDK"
EXPIRES_AT_ACCESS_TOKEN = 1440
EXPIRES_AT_REFRESH_TOKEN = 43200