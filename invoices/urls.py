from django.urls import include, path
from rest_framework import routers

from invoices.views import InvoiceViewSet, elastic_health_check, search_invoices, SearchByNumberAPIView, SearchByCompaniesNamesAPIView, SearchByDatesAPIView, SearchByDescribeProductsAPIView

router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('elastic/health-check', elastic_health_check),
    path('invoices/search', search_invoices),
    path('invoices/search-by-number', SearchByNumberAPIView.as_view()),
    path('invoices/search-by-companies-name', SearchByCompaniesNamesAPIView.as_view()),
    path('invoices/search-by-dates', SearchByDatesAPIView.as_view()),
    path('invoices/search-by-describes-products', SearchByDescribeProductsAPIView.as_view()),
]
