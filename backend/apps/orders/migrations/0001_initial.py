# Generated by Django 4.2.6 on 2023-11-18 23:01

import django.contrib.postgres.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="email address"),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (1, "in selection"),
                            (2, "awaiting payment"),
                            (3, "payed"),
                            (4, "confirmed"),
                            (5, "sent"),
                            (6, "completed"),
                        ],
                        default=1,
                        verbose_name="status",
                    ),
                ),
                (
                    "tracking_numbers",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=128),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "shipping_fee",
                    models.FloatField(default=0.0, verbose_name="shipping fee"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now=True, verbose_name="created at"),
                ),
                (
                    "last_update",
                    models.DateTimeField(auto_now=True, verbose_name="last update"),
                ),
            ],
        ),
    ]
