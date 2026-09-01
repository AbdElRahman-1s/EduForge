from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ReviewListPagination(PageNumberPagination):
    page_size = 5

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "results": data,
            }
        )
