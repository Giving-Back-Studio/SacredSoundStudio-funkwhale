import django_filters.rest_framework
from django.db.models import functions
from rest_framework import viewsets

from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters, models, serializers


class TagCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"
    queryset = (
        models.TagCategory.objects.all()
        .annotate(__size=functions.Length("name"))
        .order_by("order", "name")
    )
    serializer_class = serializers.TagCategorySerializer
    permission_classes = [oauth_permissions.ScopePermission]
    required_scope = "libraries"
    anonymous_policy = "setting"
    filterset_class = filters.TagCategoryFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"
    queryset = (
        models.Tag.objects.all()
        .annotate(__size=functions.Length("name"))
        .order_by("name")
    )
    serializer_class = serializers.TagSerializer
    permission_classes = [oauth_permissions.ScopePermission]
    required_scope = "libraries"
    anonymous_policy = "setting"
    filterset_class = filters.TagFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
