# Generated by Django 2.2.9 on 2020-01-20 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0047_auto_20200116_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='downloads_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='upload',
            name='downloads_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
