# Generated by Django 3.2.25 on 2025-01-24 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('tags', '0011_taggeditem_tag_category'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='taggeditem',
            unique_together={('tag', 'content_type', 'object_id', 'tag_category')},
        ),
    ]
