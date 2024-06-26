# Generated by Django 4.2.7 on 2024-04-06 21:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('step', '0014_alter_products_product_picture_alter_purchase_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='mode_of_payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.CharField(max_length=11)),
            ],
        ),
        migrations.AlterField(
            model_name='purchase',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='sells',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_sold', models.IntegerField()),
                ('total', models.IntegerField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='step.customer')),
                ('mode_of_payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='step.mode_of_payment')),
                ('product_sold', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='step.products')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
