from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

import math

class ElasticPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    last_page = 0
    next = ''
    previous = None

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.page_size = self.get_page_size(request)
        self.page_number = self.get_page_number(request, None)

        self.count = queryset.count()
        self.offset = (int(self.page_number) - 1) * self.page_size
        self.limit = self.page_size
        self.last_page = (math.ceil(self.count / self.limit))
        # TODO: add next, previous

        return queryset[self.offset:self.offset + self.limit].execute()
    
    def get_paginated_response(self, data):
        return Response({
            'results': data,
            'count': self.count,
            'page_size': self.page_size,
            'page': self.page_number,
            'last_page': self.last_page,
        }, status=status.HTTP_200_OK)