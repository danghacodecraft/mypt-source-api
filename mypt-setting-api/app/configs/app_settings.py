AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

ROUTES_PREFIX = "mypt-setting-api/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "test-get-user-session",
        "/" + ROUTES_PREFIX + "configs",
        "/" + ROUTES_PREFIX + "add-log",
        "/" + ROUTES_PREFIX + "add-or-update-last-change",
        "/" + ROUTES_PREFIX + "get-all-functions"
    ]
}


MYPT_AUTH_API_VER = "v1"
MYPT_AUTH_LOCAL_DOMAIN_NAME = "http://mypt.local:5559"
MYPT_AUTH_STAGING_DOMAIN_NAME = "http://mypt-auth-api-staging"
MYPT_AUTH_PRODUCTION_DOMAIN_NAME = "http://mypt-auth-api"