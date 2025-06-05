import math
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'current': self.page.number,
            'total': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'result': data, 
        })
class PostPaginattion(StandardPagination):
    page_size = 10

       

class LikesPaginattion(StandardPagination):
    page_size = 20

class commentsPaginattion(StandardPagination):
    page_size = 10
