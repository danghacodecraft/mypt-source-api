AES_SECRET_KEY = "kds592jcw016brkq"

JWT_SECRET_KEY = "ov37kpFWsz81ks5dPmXgjU"

SERVICE_NAME = 'mypt-cushomemodel-api'

ROUTES_PREFIX = SERVICE_NAME + '/v1/'

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    'authenusermiddleware': [
        '/' + ROUTES_PREFIX + 'types-models',
        '/' + ROUTES_PREFIX + 'calculate-model-equipment',
        '/' + ROUTES_PREFIX + 'scan-image',
        '/' + ROUTES_PREFIX + 'simulate-wifi',
        '/' + ROUTES_PREFIX + 'transform-image',
        '/' + ROUTES_PREFIX + 'current-equipments-info-list',
        '/' + ROUTES_PREFIX + 'create-model-survey',
        '/' + ROUTES_PREFIX + 'update-model-survey',
        '/' + ROUTES_PREFIX + 'get-history-model-survey',
        '/' + ROUTES_PREFIX + 'get-detail-model-survey',
        '/' + ROUTES_PREFIX + 'get-current-model-survey',
        '/' + ROUTES_PREFIX + 'create-house-model',
        '/' + ROUTES_PREFIX + 'update-house-model',
        '/' + ROUTES_PREFIX + 'current-house-model',
        '/' + ROUTES_PREFIX + 'detail-house-model',
        '/' + ROUTES_PREFIX + 'create-recommended-equipment',
    ],
    'userpermissionmiddleware': [

    ],
    'contractcodevalidatemiddleware': [
        '/' + ROUTES_PREFIX + 'calculate-model-equipment',
        '/' + ROUTES_PREFIX + 'current-equipments-info-list',
        '/' + ROUTES_PREFIX + 'create-model-survey',
        '/' + ROUTES_PREFIX + 'update-model-survey',
        '/' + ROUTES_PREFIX + 'get-current-model-survey',
        '/' + ROUTES_PREFIX + 'get-history-model-survey',
        '/' + ROUTES_PREFIX + 'create-house-model',
        '/' + ROUTES_PREFIX + 'update-house-model',
        '/' + ROUTES_PREFIX + 'current-house-model',

    ]
}
