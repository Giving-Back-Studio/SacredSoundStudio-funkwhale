from django.contrib.contenttypes.models import ContentType
from django import forms

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
        fields = ['name', 'max_tags', 'content_type', 'required']

    content_type = ContentTypeSelectField()


class CategorySelectField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            queryset=models.TagCategory.objects.all(), 
            *args, 
            **kwargs
        )


class TagModelForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ['name', 'category']

    # Customize a specific field
    category = CategorySelectField()


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "creation_date"]
    search_fields = ["name"]
    list_filter = ["category"]
    list_select_related = True
    form = TagModelForm


@admin.register(models.TagCategory)
class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "creation_date", "content_type"]
    search_fields = ["name"]
    list_select_related = True
    form = TagCategoryModelForm


@admin.register(models.TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ["object_id", "content_type", "tag", "creation_date"]
    search_fields = ["tag__name"]
    list_filter = ["content_type"]
    list_select_related = True
