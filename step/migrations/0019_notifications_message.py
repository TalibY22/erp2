# Generated by Django 3.2.19 on 2024-06-11 10:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('step', '0018_auto_20240611_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='Message',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]