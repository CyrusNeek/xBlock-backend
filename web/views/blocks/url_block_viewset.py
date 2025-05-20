from rest_framework import viewsets
from ...models import URLBlock
from ...serializers import URLBlockSerializer


class URLBlockViewSet(viewsets.ModelViewSet):
    queryset = URLBlock.objects.all()
    serializer_class = URLBlockSerializer
