import os

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from datetime import datetime

from ..documents import InvoiceDocument
from ..serializers import InvoiceElasticsearchSerializer
from ..pagination import ElasticPagination
from utils.elasticsearch import validate_sort_fields


def validate_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid date format: {date_str}, expected YYYY-MM-DD")


def apply_sorting(request: Request, results, allowed_fields=None):
    sort_by = request.GET.get('sort_by', '')
    order = request.GET.get('order', '')

    if bool(sort_by) != bool(order):
        raise ValidationError("Missing query param for sorting: sort_by or order.")

    if sort_by and allowed_fields and sort_by not in allowed_fields:
        raise ValidationError(f"Invalid sort_by field: {sort_by}")

    if sort_by and order:
        sort_field = f"-{sort_by}" if order == 'desc' else sort_by
        results = results.sort(sort_field)

    return results

@extend_schema(
    summary="Check connect with Elasticsearch",
    description="Endpoint pings host Elasticsearch and return status of connection.",
    responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}}
)
@api_view(['GET'])
def elastic_health_check(request: Request) -> Response:
    es = Elasticsearch(os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200"))

    if es.ping():
        return Response({"status": "connected"})
    else:
        return Response({"status": "not connected"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoiceSearchAPIView(APIView):
    document = InvoiceDocument
    serializer_class = InvoiceElasticsearchSerializer
    pagination_class = ElasticPagination

    def paginate_and_serialize(self, results, request: Request):
        paginator = self.pagination_class()
        paginated = paginator.paginate_queryset(results, request)
        serializer = self.serializer_class(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["invoices-search"],
    summary="Search invoices by company name (principal or recipient)",
    description=(
        "Returns a paginated list of invoices where the given company name occurs in either "
        "`principal_company_name` or `reciepient_company_name` fields. "
        "Performs a fuzzy search with `minimum_should_match=75%` and `operator=or`, "
        "so a match in either field is sufficient. Sorting is optional."
    ),
    parameters=[
        OpenApiParameter(
            name='company_name',
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description="The name (or part of the name) of the company to search for. "
                        "Matches are fuzzy and case-insensitive."
        ),
        OpenApiParameter(
            name='sort_by',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Field by which to sort results (e.g., 'issue_date'). Must be used together with `order`."
        ),
        OpenApiParameter(
            name='order',
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Sort order: either 'asc' or 'desc'. Must be used together with `sort_by`."
        ),
    ],
    responses={
        200: InvoiceElasticsearchSerializer(many=True),
        422: OpenApiExample(
            'Missing Parameter',
            value={"error": "Missing query param ?company_name=..."},
            response_only=True,
            status_codes=["422"]
        ),
    },
)
class SearchByCompaniesNamesAPIView(InvoiceSearchAPIView):
    def get(self, request: Request) -> Response:
        query = request.GET.get('company_name', '')

        if not query:
            return Response({
                "error": "Missing query param ?company_name=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        results = InvoiceDocument.search().query(
            "multi_match",
            query=query,
            fields=['principal_company_name', 'reciepient_company_name'],
            type="best_fields",
            operator="or",
            fuzziness="AUTO",
            minimum_should_match="75%"
        )

        try:
            results = apply_sorting(request, results)
        except ValidationError as error:
            return Response({"error": str(error)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return self.paginate_and_serialize(results, request)


@extend_schema(
    tags=["invoices-search"],
    summary="Searching incoives base on number",
    description="Searching incoives base on number using fuzzy search.",
    parameters=[
        OpenApiParameter(name='number', description='Invoice number', required=True, type=str),
        OpenApiParameter(name='sort_by', description='Field to sorting(e.g. created_at)', required=False, type=str),
        OpenApiParameter(name='order', description='Sorting direction: asc lub desc', required=False, type=str),
        OpenApiParameter(name='page', description='Number of pagination page', required=False, type=int),
    ],
    responses={200: InvoiceElasticsearchSerializer(many=True)}
)
class SearchByNumberAPIView(InvoiceSearchAPIView):
    def get(self, request: Request) -> Response:
        query = request.GET.get('number', '')

        if not query:
            return Response({
                "error": "Missing query param ?number=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        results = InvoiceDocument.search().query(
            "match",
            number={
                'query': query,
                'fuzziness': 'AUTO'
            }
        )

        try:
            results = apply_sorting(request, results)
        except ValidationError as error:
            return Response({"error": str(error)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return self.paginate_and_serialize(results, request)


@extend_schema(
    tags=["invoices-search"],
    summary="Search invoices by date range",
    description="Searches invoices based on selected date fields (`issue_date`, `payment_due_date`, `payment_date`) and a date range.",
    parameters=[
        OpenApiParameter(name="date_names", type=str, required=True, location=OpenApiParameter.QUERY, description="Comma-separated list of date fields to filter (e.g. 'issue_date,payment_date')."),
        OpenApiParameter(name="date_from", type=str, required=False, location=OpenApiParameter.QUERY, description="Start date (YYYY-MM-DD)."),
        OpenApiParameter(name="date_to", type=str, required=False, location=OpenApiParameter.QUERY, description="End date (YYYY-MM-DD)."),
    ],
    responses={
        200: InvoiceElasticsearchSerializer(many=True),
        422: OpenApiTypes.OBJECT,
    }
)
class SearchByDatesAPIView(InvoiceSearchAPIView):
    def get(self, request: Request) -> Response:
        query = request.GET.get('date_names', '')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        if not query:
            return Response({
                "error": "Missing query param ?date_names=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        if not date_from and not date_to:
            return Response({
                "error": "Missing query param ?date_from=... or ?date_to=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        date_filters = []
        date_names = query.split(',')

        if not validate_sort_fields(date_names, InvoiceDocument.ELASTIC_ALLOWED_SEARCH_FIELDS):
            return Response({
                "error": "Invalid date name field. Used inadmissible name."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


        if date_from:
            date_filters.extend([
                Q('range', issue_date={"gte": date_from}),
                Q('range', payment_due_date={"gte": date_from}),
                Q('range', payment_date={"gte": date_from}),
            ])
        if date_to:
            date_filters.extend([
                Q('range', issue_date={"lte": date_to}),
                Q('range', payment_due_date={"lte": date_to}),
                Q('range', payment_date={"lte": date_to}),
            ])

        results = InvoiceDocument.search().query(
            Q("bool", should=date_filters, minimum_should_match=1)
        )

        return self.paginate_and_serialize(results, request)


# TODO: add mappers with consts
@extend_schema(
    tags=["invoices-search"],
    summary="Search invoices by product description or name",
    description="Searches for invoices where the provided phrase appears either in the invoice `description` field or inside any `products.name` (nested field).",
    parameters=[
        OpenApiParameter(name="phrase", type=str, required=True, location=OpenApiParameter.QUERY, description="Phrase to search in description or product name."),
    ],
    responses={
        200: InvoiceElasticsearchSerializer(many=True),
        422: OpenApiTypes.OBJECT,
    }
)
class SearchByDescribeProductsAPIView(InvoiceSearchAPIView):
    def get(self, request: Request) -> Response:
        phrase = request.GET.get('phrase', '')

        if not phrase:
            return Response({
                "error": "Missing query param ?phrase=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        results = InvoiceDocument.search().query(
            "bool",
            should=[
                Q("match", description=phrase),
                Q("nested", path="products", query=Q("match", **{"products.name": phrase}))
            ],
            minimum_should_match=1
        )

        return self.paginate_and_serialize(results, request)
