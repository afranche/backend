# Generated by Django 4.2.6 on 2023-11-18 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_magiclink_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='magiclink',
            name='expires_at',
            field=models.DateTimeField(default='2023-11-18 02:43:58.583572'),
        ),
    ]
