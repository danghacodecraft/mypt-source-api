from rest_framework.response import Response

def response_data(data=None, status=1, message="Success"):
    result = {
        'statusCode': status,
        'message': message,
        'data': data
    }
    return Response(result)