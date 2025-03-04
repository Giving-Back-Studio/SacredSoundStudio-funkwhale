# Generated by Django 2.0.9 on 2018-12-05 09:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("federation", "0013_auto_20181226_1935")]

    operations = [
        migrations.CreateModel(
            name="Domain",
            fields=[
                (
                    "name",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                (
                    "creation_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="actor",
            name="domain",
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.RenameField("actor", "domain", "old_domain"),
        migrations.AddField(
            model_name="actor",
            name="domain",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="actors",
                to="federation.Domain",
            ),
        ),
        migrations.AlterUniqueTogether(name="actor", unique_together=set()),
        migrations.AlterUniqueTogether(
            name="actor", unique_together={("domain", "preferred_username")}
        ),
    ]
