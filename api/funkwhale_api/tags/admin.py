from django.contrib.contenttypes.models import ContentType
from django import forms
from admin_sort.admin import SortableAdminMixin

from funkwhale_api.common import admin

from . import models


TAGGABLE_CONTENT_TYPES = [
    "track",
]


class ContentTypeSelectField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            queryset=ContentType.objects.filter(
                app_label="music", model__in=TAGGABLE_CONTENT_TYPES,
            ), 
            *args, 
            **kwargs
        )

    def label_from_instance(self, obj):
        return f"{obj.app_label}.{obj.model}"


class TagCategoryModelForm(forms.ModelForm):
    class Meta:
        model = models.TagCategory
        fields = ['name', 'max_tags', 'content_type', 'required', 'order']

    content_type = ContentTypeSelectField()


class TagCategoryInline(admin.StackedInline):
    model = models.TagCategory
    filter_horizontal = ('tags',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "creation_date"]
    search_fields = ["name"]
    list_filter = ["categories"]
    list_select_related = True
    filter_horizontal = ('categories',)


@admin.register(models.TagCategory)
class TagCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "creation_date", "content_type"]
    search_fields = ["name"]
    position_field = 'order'
    list_select_related = True
    form = TagCategoryModelForm


@admin.register(models.TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ["object_id", "content_type", "tag", "creation_date"]
    search_fields = ["tag__name"]
    list_filter = ["content_type"]
    list_select_related = True
