from django.conf import settings
from rest_framework import serializers

from . import models



class TagCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TagCategory
        fields = ["name", "creation_date", "max_tags", "required"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["name", "creation_date"]


class TaggedItemSerializer(serializers.Serializer):
    tag = serializers.CharField()
    tag_category = serializers.CharField()


class TagNameField(serializers.CharField):
    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        if not models.TAG_REGEX.match(value):
            raise serializers.ValidationError(f'Invalid tag "{value}"')
        return value


class TagsListField(serializers.ListField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("min_length", 0)
        kwargs.setdefault("child", TagNameField())
        super().__init__(*args, **kwargs)

    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        if not value:
            return value
        # we ignore any extra tags if the length of the list is higher
        # than our accepted size
        return value[: settings.TAGS_MAX_BY_OBJ]


class CategorizedTagsField(serializers.DictField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("child", serializers.ListField(child=TagNameField()))
        super().__init__(*args, **kwargs)

    def to_internal_value(self, value):

        if isinstance(value, list) and value and isinstance(value[0], dict) and value[0].get("tag"):
            # This is a list of dictionaries, we can assume the format is correct
            return value

        if not isinstance(value, dict):
            raise serializers.ValidationError("Expected a dictionary of category names to tag lists")

        validated_data = {}
        for category_name, tags in value.items():
            try:
                category = models.TagCategory.objects.get(name=category_name)
            except models.TagCategory.DoesNotExist:
                raise serializers.ValidationError(f"Tag category '{category_name}' does not exist")

            # Validate tags list for this category
            if len(tags) > category.max_tags:
                raise serializers.ValidationError(
                    f"Category '{category_name}' allows maximum {category.max_tags} tags"
                )

            # Store validated tags with their category
            validated_tags = super().to_internal_value({category_name: tags})[category_name]
            validated_data[category_name] = validated_tags

        return [
            {"tag": tag, "tag_category": category}
            for category, tags in validated_data.items()
            for tag in tags
        ]
