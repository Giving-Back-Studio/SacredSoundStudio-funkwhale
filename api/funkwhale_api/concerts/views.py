from rest_framework import viewsets, permissions

from .models import Concert
from .serializers import ConcertSerializer

class ConcertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer
    permission_classes = [permissions.IsAuthenticated]