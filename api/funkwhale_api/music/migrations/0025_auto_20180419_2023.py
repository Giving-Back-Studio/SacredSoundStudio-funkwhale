# Generated by Django 2.0.3 on 2018-04-19 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("music", "0024_populate_uuid")]

    operations = [
        migrations.AlterField(
            model_name="trackfile",
            name="source",
            field=models.URLField(blank=True, max_length=500, null=True),
        )
    ]
