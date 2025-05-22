from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from web.models import LLMChat
from web.serializers import LLMChatSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta


class FixedSizeResultsSetPagination(PageNumberPagination):
    page_size = 11
    
class LLMChatFilter(filters.FilterSet):
    message_search = filters.CharFilter(method='filter_message_search')
    
    class Meta:
        model = LLMChat
        fields = []

    def filter_message_search(self, queryset, name, value):
        # Use the `__icontains` lookup to search the entire JSON string for the keyword
        # This does not parse the JSON structure but treats it as a plain string
        return queryset.filter(messages__icontains=value)

class LLMChatViewSet(viewsets.ModelViewSet):
    serializer_class = LLMChatSerializer
    permission_classes = [IsAuthenticated]
    queryset = LLMChat.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = LLMChatFilter
    pagination_class = FixedSizeResultsSetPagination  # Ensure this is set

    def get_queryset(self):
        one_week_ago = timezone.now() - timedelta(days=7)
        return LLMChat.objects.filter(
            user=self.request.user,
            created_at__gte=one_week_ago
        ).order_by('-created_at')
