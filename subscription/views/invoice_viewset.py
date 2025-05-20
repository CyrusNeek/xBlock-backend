from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from subscription.models import Invoice
from subscription.serializers import InvoiceSerializer
from rest_framework.pagination import PageNumberPagination


class InvoicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class InvoiceViewSet(
    ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    """
    ViewSet for listing and retrieving Invoices.
    """
    permission_classes = [IsAuthenticated]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    pagination_class = InvoicePagination

    def get_queryset(self):
        invoices = Invoice.objects.filter(client=self.request.user)
        return invoices
