# Generated by Django 2.0.6 on 2018-06-22 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0027_auto_20180515_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='importjob',
            name='replace_if_duplicate',
            field=models.BooleanField(default=False),
        ),
    ]
