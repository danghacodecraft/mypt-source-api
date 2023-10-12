AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-company-api"

ROUTES_PREFIX = SERVICE_NAME + "/v1/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "logout",
        "/" + ROUTES_PREFIX + "get-list-idea",
        "/" + ROUTES_PREFIX + "get-list-comment",
        "/" + ROUTES_PREFIX + "post-create-blogs",
        "/" + ROUTES_PREFIX + "post-create-evaluate",
        "/" + ROUTES_PREFIX + "list-idea",
        "/" + ROUTES_PREFIX + "list-comment",
        "/" + ROUTES_PREFIX + "create-comment",
        "/" + ROUTES_PREFIX + "edit-comment",
        "/" + ROUTES_PREFIX + "detele-comment",
        "/" + ROUTES_PREFIX + "home-count-ptq",
        "/" + ROUTES_PREFIX + "history-ptq",
        "/" + ROUTES_PREFIX + "history-ptq-id",
        "/" + ROUTES_PREFIX + "ptq-type",
        "/" + ROUTES_PREFIX + "explanation",
    ],
    "userpermissionmiddleware": [
        # "/" + ROUTES_PREFIX + "get-list-idea",
        # "/" + ROUTES_PREFIX + "get-list-comment",
        # "/" + ROUTES_PREFIX + "post-create-blogs",
        # "/" + ROUTES_PREFIX + "post-create-evaluate",
        # "/" + ROUTES_PREFIX + "list-idea",
        # "/" + ROUTES_PREFIX + "list-comment",
        # "/" + ROUTES_PREFIX + "create-comment",
        # "/" + ROUTES_PREFIX + "edit-comment",
        # "/" + ROUTES_PREFIX + "detele-comment"
    ]
}
