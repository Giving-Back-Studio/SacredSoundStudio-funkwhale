# Generated by Django 3.2.25 on 2025-01-24 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0058_auto_20250124_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='record_label',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='release_date',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
