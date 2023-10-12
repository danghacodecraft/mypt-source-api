SERVICE_CONFIG = {
    "survey":{
        "base_http": "http://survey.fpt.vn/",
        "getDetailPointEmp": "api/v1/get-detail-point-emp",
        "method": "POST"
    },
    "fcm":{
        "base_http": "https://fcm.googleapis.com/",
        "sent":"fcm/send",
        "method": "POST",
        "server_key": "AAAAt8aIEiQ:APA91bEIqBfqTHI0-0xavXrh0U7CJguWaQXZ1CTBmpNHgEkI6ciV7QrRTlzyckRhDkM9lMw2RDfqdc7rkGHD6pMxl5z9IZ4nOE_n6AtNkyNPRlEgRImZ1ipMPZekmX26TWAbf3WYxLOM",
    },
    "auth":{
        "base_http_local": "http://myptpdx-api-stag.fpt.net/mypt-auth-api/v1/",
        "base_http_staging": "http://mypt-auth-api-staging/mypt-auth-api/v1/",
        "base_http_production": "http://mypt-auth-api/mypt-auth-api/v1/",
        "get-user-device-info-by-email": {
            "func" : "get-user-device-info-by-email",
            "method" : "POST"
        },
        "get-user-devices-info-by-emails":{
            "func" : "get-user-devices-info-by-emails",
            "method" : "POST"
        },
        "get-emails-by-device-tokens" : {
            "func" : "get-emails-by-device-tokens",
            "method" : "POST"
        }
    },
    "profile":{
        "base_http_local": "http://mypt.local/mypt-profile-api/v1/",
        "base_http_staging": "http://myptpdx-api-stag.fpt.net/mypt-profile-api/v1/",
        "base_http_production": "http://myptpdx-api.fpt.net/mypt-profile-api/v1/",
        "email-to-list-code": {
            "func" : "email-to-list-code",
            "method" : "POST"
        }
    }
}
