# Generated by Django 5.0.3 on 2024-03-22 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('step', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Business',
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.DeleteModel(
            name='Supplier',
        ),
    ]
