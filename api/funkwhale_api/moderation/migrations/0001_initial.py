# Generated by Django 2.0.9 on 2019-01-07 06:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('federation', '0016_auto_20181227_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstancePolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('summary', models.TextField(blank=True, max_length=10000, null=True)),
                ('block_all', models.BooleanField(default=False)),
                ('silence_activity', models.BooleanField(default=False)),
                ('silence_notifications', models.BooleanField(default=False)),
                ('reject_media', models.BooleanField(default=False)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_instance_policies', to='federation.Actor')),
                ('target_actor', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='instance_policy', to='federation.Actor')),
                ('target_domain', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='instance_policy', to='federation.Domain')),
            ],
        ),
    ]
