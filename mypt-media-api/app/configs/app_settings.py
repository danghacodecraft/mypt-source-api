AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-media-api"

ROUTES_PREFIX = SERVICE_NAME + "/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "view-file-auth",
        "/" + ROUTES_PREFIX + "upload-file",
        "/" + ROUTES_PREFIX + "view-image-iqc"
    ],
    "userpermissionmiddleware": [
    ]
}



