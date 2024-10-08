# Generated by Django 4.2.5 on 2023-10-25 21:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("Product", "0005_alter_historicalproduct_sku_alter_product_sku"),
    ]

    operations = [
        migrations.CreateModel(
            name="InputOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="InputOrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=0)),
                (
                    "outputOrder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="InputHistory.inputorder",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Product.product",
                    ),
                ),
            ],
        ),
    ]
