from drf_spectacular.utils import OpenApiResponse, OpenApiExample

BASE_DESCRIPTION = """
- Authorization : Bearer {access token}

- Content-Type: application/json.
"""


CREATE_BLOG_DESCRIPTION = """
Viết đánh giá xe cải tiến về app MyPT
""" + BASE_DESCRIPTION

HOME_COUNT_DESCRIPTION = """
Đếm kiểm soát màn hình home
""" + BASE_DESCRIPTION

HOME_COUNT_2_DESCRIPTION = """
Đếm kiểm soát màn hình home version 2
""" + BASE_DESCRIPTION

RESPONSE_EXAMPLE_HOME_COUNT_SUCCESS = {
    "statusCode": 1,
    "message": "Success",
    "data": {
        "deadline": 0,
        "needExplanation": 0,
        "addExplanation": 0
    }
}

RESPONSE_EXAMPLE_HOME_COUNT_FAIL = {
    "statusCode": 5,
    "message": "Token không có thông tin",
    "data": None
}

RESPONSE_EXAMPLE_HOME_COUNT_2_SUCCESS = {
    "statusCode": 1,
    "message": "Success",
    "data": {
        "deadline": {
            "data": 0,
            "name": "Sắp hết hạn",
            "type": "ALL",
            "searchKey": [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8
            ]
        },
        "needExplanation": {
            "data": 0,
            "name": "Chưa giải trình",
            "type": "NOTOK",
            "searchKey": [
                2
            ]
        },
        "addExplanation": {
            "data": 0,
            "name": "Bổ sung giải trình",
            "type": "ADD",
            "searchKey": [
                7
            ]
        }
    }
}

RESPONSE_EXAMPLE_HOME_COUNT = {
    200: OpenApiResponse(
        description='Example',
        response=RESPONSE_EXAMPLE_HOME_COUNT_SUCCESS,
        examples=[
            OpenApiExample(
                name='Success',
                value=RESPONSE_EXAMPLE_HOME_COUNT_SUCCESS),
            OpenApiExample(
                name='Fail',
                value=RESPONSE_EXAMPLE_HOME_COUNT_FAIL)
        ]
    )
}

RESPONSE_EXAMPLE_HOME_COUNT_2 = {
    200: OpenApiResponse(
        description='Example',
        response=RESPONSE_EXAMPLE_HOME_COUNT_2_SUCCESS,
        examples=[
            OpenApiExample(
                name='Success',
                value=RESPONSE_EXAMPLE_HOME_COUNT_2_SUCCESS),
            OpenApiExample(
                name='Fail',
                value=RESPONSE_EXAMPLE_HOME_COUNT_FAIL)
        ]
    )
}