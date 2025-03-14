# Generated by Django 3.2.25 on 2025-01-17 06:05

import django.contrib.postgres.fields.citext
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_auto_20200803_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', django.contrib.postgres.fields.citext.CICharField(max_length=100, unique=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='tag',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='tags.tagcategory'),
        ),
    ]
