from rest_framework.response import Response
from ...core.helpers.global_variable import *

from math import ceil


def response_data(data="", status=1, message="Success"):
    result = {
        'statusCode': status,
        'message': message,
        'data': data
    }
    return Response(result)


def response_datas(data="", status=1, message="Success", number=0):
    result = {
        'statusCode': status,
        'message': message,
        'data': {
            'numberPage': number,
            'listData': data
        }
    }
    return Response(result)

def response_paginator(sum, per_page, data):
    result = {
        'maxPage': ceil(sum/per_page),
        'listData': data
    }
    return response_data(data=result)


def response_error(status=503, data=None):
    if status not in RESPONSE_MESSAGES.keys():
        status = 503
    result = {
        'statusCode': status,
        'message': RESPONSE_MESSAGES[status],
        'data': data
    }
    return Response(result)
