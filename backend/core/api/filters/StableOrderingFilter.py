from typing import TypeVar

from django.db.models import (
    Model,
    QuerySet,
)
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.views import APIView

_ModelT = TypeVar("_ModelT", bound=Model)
_RowT = TypeVar("_RowT")


class StableOrderingFilter(OrderingFilter):
    #   Desempata pelo pk: sem isso, itens com o mesmo valor (ex.: mesmo preço) podem
    #   se repetir ou sumir entre uma página e outra da paginação.
    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet[_ModelT, _RowT],
        view: APIView,
    ) -> QuerySet[_ModelT, _RowT]:
        ordered = super().filter_queryset(request, queryset, view)
        ordering = ordered.query.order_by

        if not ordering:
            return ordered

        first = ordering[0]
        tie_breaker = "-pk" if isinstance(first, str) and first.startswith("-") else "pk"

        return ordered.order_by(*ordering, tie_breaker)
