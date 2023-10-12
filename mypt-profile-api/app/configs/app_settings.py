AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

ROUTES_PREFIX = "mypt-profile-api/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "employee",
        "/" + ROUTES_PREFIX + "employee-new",
        "/" + ROUTES_PREFIX + "get-all-profile",
        "/" + ROUTES_PREFIX + "get-all-profile-new",
        "/" + ROUTES_PREFIX + "get-profile-overview",
        "/" + ROUTES_PREFIX + "get-profile-detail",
        "/" + ROUTES_PREFIX + "get-working-information",
        "/" + ROUTES_PREFIX + "get-salary-account",
        "/" + ROUTES_PREFIX + "get-insurance-tax",
        "/" + ROUTES_PREFIX + "get-contracts",
        "/" + ROUTES_PREFIX + "get-occupational-safety-card",
        "/" + ROUTES_PREFIX + "get-application-info",
        "/" + ROUTES_PREFIX + "get-device-info",
        "/" + ROUTES_PREFIX + "update-avatar",
        "/" + ROUTES_PREFIX + "update-birthday-profile",
        "/" + ROUTES_PREFIX + "salary-auth",
        "/" + ROUTES_PREFIX + "salary-check-otp",
        "/" + ROUTES_PREFIX + "salary-change-password",
    ],
}

SALARY_SECRET_KEY = 'dPFH6xlrOoHoSL5B'
