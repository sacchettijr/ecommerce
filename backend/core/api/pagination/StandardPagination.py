from typing import (
    Any,
    cast,
)

from django.core.paginator import Page
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    def get_paginated_response(
        self,
        data: Any,
    ) -> Response:
        page = cast("Page[Any]", self.page)

        return Response(
            data={
                "count": page.paginator.count,
                "total_pages": page.paginator.num_pages,
                "current_page": page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
        )
