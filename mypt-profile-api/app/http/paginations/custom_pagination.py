from rest_framework import pagination
from rest_framework.response import Response
import math


class StandardPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class CustomPagination(StandardPagination):
    def get_paginated_response(self, data):
        return Response({
            "pageNumber": math.ceil(self.page.paginator.count / self.get_page_size(self.request)),
            "results": data
        })
