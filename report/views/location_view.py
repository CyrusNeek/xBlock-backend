from rest_framework.generics import ListAPIView
from report.serializers import LocationSerializer
from web.models import Unit
from django.db.models import Q


class LocationView(ListAPIView):
    serializer_class = LocationSerializer
    queryset = Unit.objects.all()

    def get_queryset(self):
        return Unit.objects.accessible_by_user(self.request.user)
