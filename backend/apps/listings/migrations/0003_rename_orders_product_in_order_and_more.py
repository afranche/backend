# Generated by Django 4.2.6 on 2023-11-18 15:54

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0002_coupon"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="orders",
            new_name="in_order",
        ),
        migrations.AlterField(
            model_name="coupon",
            name="applied_to",
            field=models.ManyToManyField(
                default=django.db.models.manager.BaseManager.all,
                to="listings.listing",
                verbose_name="Applied to",
            ),
        ),
        migrations.AlterField(
            model_name="listing",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
