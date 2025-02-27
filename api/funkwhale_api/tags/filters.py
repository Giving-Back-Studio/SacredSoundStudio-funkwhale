import django_filters
from django.db import models as dj_models
from django_filters import rest_framework as filters

from funkwhale_api.common import fields

from . import models


class TagFilter(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["name"])
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("creation_date", "creation_date"),
            ("__size", "length"),
        )
    )

    class Meta:
        model = models.Tag
        fields = {"name": ["exact", "startswith"], "categories__name": ["exact"]}


class TagCategoryFilter(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["name"])
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("creation_date", "creation_date"),
            ("content_type", "content_type"),
            ("__size", "length"),
        )
    )

    class Meta:
        model = models.TagCategory
        fields = {"name": ["exact"], "content_type__model": ["exact"]}


def get_by_similar_tags(qs, tags):
    """
    Return a queryset of objects with at least one matching tag.
    Annotate the queryset so you can order later by number of matches.
    """
    qs = qs.filter(tagged_items__tag__name__in=tags).annotate(
        tag_matches=dj_models.Count(
            dj_models.Case(
                dj_models.When(tagged_items__tag__name__in=tags, then=1),
                output_field=dj_models.IntegerField(),
            )
        )
    )
    return qs.distinct()
