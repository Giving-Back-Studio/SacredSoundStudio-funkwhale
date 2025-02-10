import re

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import CICharField
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

TAG_REGEX = re.compile(r"^([\w\s()/]+)$")


class TagCategory(models.Model):
    name = CICharField(max_length=100)
    creation_date = models.DateTimeField(default=timezone.now)
    max_tags = models.PositiveIntegerField(default=5)
    required = models.BooleanField(default=False)
    content_type = models.ForeignKey(
        ContentType, null=True, on_delete=models.SET_NULL,
    )
    order = models.PositiveSmallIntegerField(
        default=0, blank=False, null=False,
    )

    class Meta:
        unique_together = ("name", "content_type")
        ordering = ('order', 'name', )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = CICharField(max_length=100)
    creation_date = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(TagCategory, related_name="tags", blank=True)

    def __str__(self):
        return self.name


class TaggedItemQuerySet(models.QuerySet):
    def for_content_object(self, obj):
        return self.filter(
            object_id=obj.id,
            content_type__app_label=obj._meta.app_label,
            content_type__model=obj._meta.model_name,
        )


class TaggedItem(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    tag = models.ForeignKey(Tag, related_name="tagged_items", on_delete=models.CASCADE)
    tag_category = models.ForeignKey(TagCategory, null=True, on_delete=models.SET_NULL)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content type"),
        related_name="tagged_items",
    )
    object_id = models.IntegerField(verbose_name=_("Object id"), db_index=True)
    content_object = GenericForeignKey()

    objects = TaggedItemQuerySet.as_manager()

    class Meta:
        unique_together = ("tag", "content_type", "object_id", "tag_category")

    def __str__(self):
        return self.tag.name


@transaction.atomic
def add_tags(obj, *tags):
    if not tags:
        return
    tag_objs = [Tag(name=t) for t in tags]
    Tag.objects.bulk_create(tag_objs, ignore_conflicts=True)
    tag_ids = Tag.objects.filter(name__in=tags).values_list("id", flat=True)

    tagged_items = [TaggedItem(tag_id=tag_id, content_object=obj) for tag_id in tag_ids]

    TaggedItem.objects.bulk_create(tagged_items, ignore_conflicts=True)


@transaction.atomic
def set_tags(obj, *tags):
    # we ignore any extra tags if the length of the list is higher
    # than our accepted size
    tags = tags[: settings.TAGS_MAX_BY_OBJ]
    tags = set(tags)
    existing = set(
        TaggedItem.objects.for_content_object(obj).values_list("tag__name", flat=True)
    )
    found = tags & existing
    to_add = tags - found
    to_remove = existing - (found | to_add)

    add_tags(obj, *to_add)
    remove_tags(obj, *to_remove)


@transaction.atomic
def remove_tags(obj, *tags):
    if not tags:
        return
    TaggedItem.objects.for_content_object(obj).filter(tag__name__in=tags).delete()


@transaction.atomic
def set_categorized_tags(obj, tagged_items):
    """
    Set tags with their categories for an object.
    
    Args:
        obj: The object to tag
        tagged_items: List of dicts with 'tag' and 'tag_category' keys
    """
    if not tagged_items:
        # Remove all existing tags if no new tags provided
        TaggedItem.objects.for_content_object(obj).delete()
        return

    # Create any missing tags
    tag_names = {item['tag'] for item in tagged_items}
    tag_objs = [Tag(name=name) for name in tag_names]
    Tag.objects.bulk_create(tag_objs, ignore_conflicts=True)

    # Get tag and category mappings
    tags = {t.name: t for t in Tag.objects.filter(name__in=tag_names)}
    categories = {
        c.name: c for c in TagCategory.objects.filter(
            name__in={item['tag_category'] for item in tagged_items}
        )
    }

    # Prepare new tagged items
    new_items = []
    for item in tagged_items:
        tag = tags[item['tag']]
        category = categories[item['tag_category']]
        new_items.append(
            TaggedItem(
                tag=tag,
                tag_category=category,
                content_object=obj
            )
        )

    # Remove existing tags and add new ones
    TaggedItem.objects.for_content_object(obj).delete()
    TaggedItem.objects.bulk_create(new_items, ignore_conflicts=True)
