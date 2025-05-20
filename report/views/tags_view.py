from report.serializers import TagSerializer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from report.models import Tag
from web.models import Unit
from django.db.models import Q


class TagsView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        units = Unit.objects.accessible_by_user(self.request.user)
        return super().get_queryset().filter(user__unit__in=units)
