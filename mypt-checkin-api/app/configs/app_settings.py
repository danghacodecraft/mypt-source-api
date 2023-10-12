AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-checkin-api"

ROUTES_PREFIX = SERVICE_NAME + "/v2/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [

        "/" + ROUTES_PREFIX + "get-coordinate",
        "/" + ROUTES_PREFIX + "provide-info-device",
        "/" + ROUTES_PREFIX + "get-info-emp-checkin",
        # "/" + ROUTES_PREFIX + "refresh-data-checkin",
        # "/" + ROUTES_PREFIX + "refresh-data-device",
        "/" + ROUTES_PREFIX + "confirm-info-checkin",
        "/" + ROUTES_PREFIX + "list-response",
        "/" + ROUTES_PREFIX + "send-response",
        "/" + ROUTES_PREFIX + "report-checkin-on-month"
    ],
    "userpermissionmiddleware": [
        "/" + ROUTES_PREFIX + "get-coordinate",
        "/" + ROUTES_PREFIX + "provide-info-device",
        "/" + ROUTES_PREFIX + "get-info-emp-checkin",
        "/" + ROUTES_PREFIX + "confirm-info-checkin",
        "/" + ROUTES_PREFIX + "list-response",
        "/" + ROUTES_PREFIX + "send-response",
        "/" + ROUTES_PREFIX + "report-checkin-on-month"
    ]
}

