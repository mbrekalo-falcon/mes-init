"""

    This script will contain all function for REST API.

"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def rest_default_response(data=None, status=None, message=None, custom_status=None):
    return Response(
        data={
            "data": data,
            "code": status,
            "message": message,
            "custom_status": custom_status
        },
        status=status
    )


class StandardApplicationSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
