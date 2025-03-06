from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Concert
from .serializers import ConcertSerializer

class ConcertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer