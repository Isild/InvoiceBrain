import os

from django.http import JsonResponse
from elasticsearch import Elasticsearch
from rest_framework import viewsets
from rest_framework.decorators import api_view

from .documents import InvoiceDocument
from .models import Invoice
from .serializers import InvoiceSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

@api_view(['GET'])
def elastic_check(request):
    es = Elasticsearch(os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200"))

    if es.ping():
        return JsonResponse({"status":"connected"})
    else:
        return JsonResponse({"status":"not connected"}, status=500)

@api_view(['GET'])
def search_invoices(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'created_at')
    order = request.GET.get('order', 'desc')
    
    if not query:
        return JsonResponse({
            "error": "Missing query param ?q=..."
        }, status=400)
    
    results = InvoiceDocument.search().query(
        "multi_match", 
        query=query,
        fields=['principal_company_name', 'reciepient_company_name']
    )
    # results = InvoiceDocument.search().query(
    #     "match", 
    #     number=query
    # )
    # results = InvoiceDocument.search().query(
    #     "match", 
    #     number={
    #         'query':query,
    #         'fuzziness':'AUTO'
    #     }
    # )


    sort_field = f"-{sort_by}" if order == 'desc' else sort_by
    results = results.sort(sort_field)

    results = results.execute()

    return JsonResponse({
        "data": [hit.to_dict() for hit in results]
    })