from rest_framework.response import Response

def response_data(data, status, message):
    result = {
        'statusCode': status,
        'message': message,
        'data': data
    }
    return Response(result)