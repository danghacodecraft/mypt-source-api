from rest_framework.response import Response

def response_data(data={}, status=1, message="Success"):
    result = {
        'status': status,
        'message': message,
        'data': data
    }
    return Response(result)