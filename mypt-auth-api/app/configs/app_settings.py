AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

ROUTES_PREFIX = "mypt-auth-api/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "timeauthmiddleware": [
        "/" + ROUTES_PREFIX + "user-token"
    ],
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "test-get-user-session",
        "/" + ROUTES_PREFIX + "get-chatbot-sender-info",
        "/" + ROUTES_PREFIX + "get-chatbot-sender-info-new",
        "/" + ROUTES_PREFIX + "proactively-update-device-token",
    ]
}

OAUTH_CLIENT_ID = "My_PT"

EXPIRES_AT_ACCESS_TOKEN = 1440
EXPIRES_AT_REFRESH_TOKEN = 43200

MYPT_PROFILE_API_VER = "v1"
MYPT_SETTING_API_VER = "v1"
MYPT_CHATBOT_API_VER = "v1"

MYPT_PROFILE_LOCAL_DOMAIN_NAME = "http://mypt.local:5553"
MYPT_PROFILE_STAGING_DOMAIN_NAME = "http://mypt-profile-api-staging"
MYPT_PROFILE_PRODUCTION_DOMAIN_NAME = "http://mypt-profile-api"

MYPT_SETTING_LOCAL_DOMAIN_NAME = "http://mypt.local:5554"
MYPT_SETTING_STAGING_DOMAIN_NAME = "http://mypt-setting-api-staging"
MYPT_SETTING_PRODUCTION_DOMAIN_NAME = "http://mypt-setting-api"

MYPT_CHATBOT_LOCAL_DOMAIN_NAME = "http://mypt.local:5546"
MYPT_CHATBOT_STAGING_DOMAIN_NAME = "http://mypt-chatbot-api-staging"
MYPT_CHATBOT_PRODUCTION_DOMAIN_NAME = "http://mypt-chatbot-api"


AZURE_CLIENT_ID = "d7962a93-e9ba-4614-868d-d65a2f5afb13"
# AZURE_CLIENT_SECRET = "V-g8Q~WbrUjch3xszWOSLNs5IpYJQ5JEGpbRqduS"
AZURE_CLIENT_SECRET = "lPW8Q~OeYjz6iKTQKt6IAvzQ~~I~DrvdOvB~Ea~v"