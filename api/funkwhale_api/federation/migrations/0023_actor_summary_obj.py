# Generated by Django 2.2.9 on 2020-01-22 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_auto_20200116_1610'),
        ('federation', '0022_auto_20191204_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='summary_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.Content'),
        ),
    ]
