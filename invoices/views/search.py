import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..documents import InvoiceDocument
from ..serializers import InvoiceSerializer
from ..pagination import ElasticPagination
from utils.elasticsearch import validate_sort_fields

@api_view(['GET'])
def elastic_health_check(request):
    es = Elasticsearch(os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200"))

    if es.ping():
        return Response({"status":"connected"})
    else:
        return Response({"status":"not connected"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_invoices(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'created_at')
    order = request.GET.get('order', 'desc')
    
    if not query:
        return Response({
            "error": "Missing query param ?q=..."
        }, status=400)
    
    results = InvoiceDocument.search().query(
        "multi_match", 
        query=query,
        fields=['principal_company_name', 'reciepient_company_name']
    )

    sort_field = f"-{sort_by}" if order == 'desc' else sort_by
    results = results.sort(sort_field)

    results = results.execute()

    return Response({
        "data": [hit.to_dict() for hit in results]
    })

class SearchByNumberAPIView(APIView):
    document = InvoiceDocument
    serializer_class = InvoiceSerializer
    pagination_class = ElasticPagination

    def get(self, request):
        query = request.GET.get('number', '')
        sort_by = request.GET.get('sort_by', '')
        order = request.GET.get('order', '')
        
        if not query:
            return Response({
                "error": "Missing query param ?number=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        

        results = InvoiceDocument.search().query(
            "match", 
            number={
                'query':query,
                'fuzziness':'AUTO'
            }
        )

        if sort_by and order:
            sort_field = f"-{sort_by}" if order == 'desc' else sort_by
            results = results.sort(sort_field)
        elif bool(sort_by) != bool(order):
            return Response({
                "error": "Missing query param for sorting: sort_by or order."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        paginator = self.pagination_class()
        results = paginator.paginate_queryset(results, request)

        serializer = InvoiceSerializer(results, many=True)

        return paginator.get_paginated_response(serializer.data)


class SearchByCompaniesNamesAPIView(APIView):
    document = InvoiceDocument
    serializer_class = InvoiceSerializer
    pagination_class = ElasticPagination

    def get(self, request):
        query = request.GET.get('company_name', '')
        sort_by = request.GET.get('sort_by', '')
        order = request.GET.get('order', '')
        
        if not query:
            return Response({
                "error": "Missing query param ?company_name=..."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        

        results = InvoiceDocument.search().query(
            "multi_match", 
            query=query,
            fields=['principal_company_name', 'reciepient_company_name'],
            type="best_fields",
            operator="and",
            fuzziness="AUTO"
        )

        if sort_by and order:
            sort_field = f"-{sort_by}" if order == 'desc' else sort_by
            results = results.sort(sort_field)
        elif bool(sort_by) != bool(order):
            return Response({
                "error": "Missing query param for sorting: sort_by or order."
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        paginator = self.pagination_class()
        results = paginator.paginate_queryset(results, request)

        serializer = InvoiceSerializer(results, many=True)

        return paginator.get_paginated_response(serializer.data)


class SearchByDatesAPIView(APIView):
    document = InvoiceDocument
    serializer_class = InvoiceSerializer
    pagination_class = ElasticPagination

    def get(self, request):
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

        paginator = self.pagination_class()
        results = paginator.paginate_queryset(results, request)

        serializer = InvoiceSerializer(results, many=True)

        return paginator.get_paginated_response(serializer.data)
    
# TODO: add mappers with consts
class SearchByDescribeProductsAPIView(APIView):
    document = InvoiceDocument
    serializer_class = InvoiceSerializer
    pagination_class = ElasticPagination

    def get(self, request):
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

        paginator = self.pagination_class()
        results = paginator.paginate_queryset(results, request)

        serializer = InvoiceSerializer(results, many=True)

        return paginator.get_paginated_response(serializer.data)
