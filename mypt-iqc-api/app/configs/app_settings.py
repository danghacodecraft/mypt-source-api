# AES_SECRET_KEY = 'pnc3976myptcjmgp'

AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-iqc-api"

IQC_SESSION_ID = "L3N0b3JhZ2UvZW11bGF0ZWQvMC9QaWN0dXJlcy9JUUMvSVFDX0lNR18yMDIyMTIxNF8xMDMyMTJfNDE1Xzg5MjgyNzAwOTYzMDM4NDQ2OTEuanBn"

ROUTES_PREFIX = SERVICE_NAME + "/v1/"
MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "check-iqc-contract",
        "/" + ROUTES_PREFIX + "toolbar-search-iqc",
        "/" + ROUTES_PREFIX + "load-iqc-album-upload-deployment",
        "/" + ROUTES_PREFIX + "get-iqc-detail-deployment",
        "/" + ROUTES_PREFIX + "create-contract-deployment",
        "/" + ROUTES_PREFIX + "update-contract-deployment",
        "/" + ROUTES_PREFIX + "load-iqc-upload-return-contract",
        "/" + ROUTES_PREFIX + "load-iqc-detail-return-contract",
        "/" + ROUTES_PREFIX + "create-or-update-return-contract",
        "/" + ROUTES_PREFIX + "get-list-return-contract-cause",
        "/" + ROUTES_PREFIX + "get-list-transaction-type",
        "/" + ROUTES_PREFIX + "get-list-house-model",

        "/" + ROUTES_PREFIX + "load-iqc-upload-practice-point",
        "/" + ROUTES_PREFIX + "load-iqc-detail-practice-point",
        "/" + ROUTES_PREFIX + "create-practice-point",
        "/" + ROUTES_PREFIX + "update-practice-point",
        "/" + ROUTES_PREFIX + "practice-point-get-cause-image",
        "/" + ROUTES_PREFIX + "upload-image",
        # "/" + ROUTES_PREFIX + "upload-image-new",
    ],
    "userpermissionmiddleware": [
        "/" + ROUTES_PREFIX + "check-iqc-contract",
        "/" + ROUTES_PREFIX + "toolbar-search-iqc",
        "/" + ROUTES_PREFIX + "load-iqc-album-upload-deployment",
        "/" + ROUTES_PREFIX + "get-iqc-detail-deployment",
        "/" + ROUTES_PREFIX + "create-contract-deployment",
        "/" + ROUTES_PREFIX + "update-contract-deployment",
        "/" + ROUTES_PREFIX + "load-iqc-upload-return-contract",
        "/" + ROUTES_PREFIX + "load-iqc-detail-return-contract",
        "/" + ROUTES_PREFIX + "create-or-update-return-contract",
        "/" + ROUTES_PREFIX + "get-list-return-contract-cause",
        "/" + ROUTES_PREFIX + "get-list-transaction-type",
        "/" + ROUTES_PREFIX + "get-list-house-model",
        "/" + ROUTES_PREFIX + "upload-image",

        "/" + ROUTES_PREFIX + "load-iqc-upload-practice-point",
        "/" + ROUTES_PREFIX + "load-iqc-detail-practice-point",
        "/" + ROUTES_PREFIX + "create-practice-point",
        "/" + ROUTES_PREFIX + "update-practice-point",
        "/" + ROUTES_PREFIX + "practice-point-get-cause-image",
    ]
}
