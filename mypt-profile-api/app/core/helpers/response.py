from rest_framework.response import Response
from ....app.core.helpers.global_data import *

def response_data(data="", status=1, message="Success"):
    result = {
        'statusCode': status,
        'message': message,
        'data': data
    }
    return Response(result)


def response_error(status=503, data = None):
    if(status not in RESPONSE_MESSAGES.keys()):
        status = 503
    result = {
        'statusCode': status,
        'message': RESPONSE_MESSAGES[status],
        'data': data
    }
    return Response(result)