# Generated by Django 2.0 on 2017-12-26 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0015_bind_track_file_to_import_job'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackfile',
            name='acoustid_track_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
