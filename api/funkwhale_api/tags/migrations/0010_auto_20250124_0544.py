# Generated by Django 3.2.25 on 2025-01-24 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0009_auto_20250124_0527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tagcategory',
            name='tags',
        ),
        migrations.AddField(
            model_name='tag',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='tags', to='tags.TagCategory'),
        ),
    ]
