# AES_SECRET_KEY = 'pnc3976myptcjmgp'

AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-job-api"

ROUTES_PREFIX = SERVICE_NAME + "/v1/"
MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "get-kpi-result",
        "/" + ROUTES_PREFIX + "get-kpi-detail-info",
        "/" + ROUTES_PREFIX + "get-kpi-list-chart",
        "/" + ROUTES_PREFIX + "get-csat-list-chart",
        # SALARY
        "/" + ROUTES_PREFIX + "get-salary-in-home",
        "/" + ROUTES_PREFIX + "get-salary-provisional-overview",
        "/" + ROUTES_PREFIX + "get-salary-provisional-by-date",
        "/" + ROUTES_PREFIX + "get-salary-formula-by-month",
        "/" + ROUTES_PREFIX + "get-salary-real-by-month",
        "/" + ROUTES_PREFIX + "salary-auth",
        "/" + ROUTES_PREFIX + "salary-check-otp",
        "/" + ROUTES_PREFIX + "salary-change-password",
        "/" + ROUTES_PREFIX + "tracking-action",
        "/" + ROUTES_PREFIX + "update-config-value-by-key",
        "/" + ROUTES_PREFIX + "clear-cache-by-prefix",
        "/" + ROUTES_PREFIX + "clear-cache-by-key",
        "/" + ROUTES_PREFIX + "show-tools",
        "/" + ROUTES_PREFIX + "add-tools",
        "/" + ROUTES_PREFIX + "count-tools-expiration",
    ],
    "userpermissionmiddleware": [
        "/" + ROUTES_PREFIX + "get-kpi-result",
        "/" + ROUTES_PREFIX + "get-kpi-detail-info",
        "/" + ROUTES_PREFIX + "get-kpi-list-chart",
        "/" + ROUTES_PREFIX + "get-csat-list-chart",
    ],
    "salarymiddleware": [
        "/" + ROUTES_PREFIX + "get-salary-provisional-overview",
        "/" + ROUTES_PREFIX + "get-salary-provisional-by-date",
        "/" + ROUTES_PREFIX + "get-salary-formula-by-month",
        "/" + ROUTES_PREFIX + "get-salary-real-by-month",
    ]
}

SALARY_SECRET_KEY = 'dPFH6xlrOoHoSL5B'
