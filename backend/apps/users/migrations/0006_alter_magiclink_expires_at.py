# Generated by Django 4.2.6 on 2023-11-17 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_magiclink_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='magiclink',
            name='expires_at',
            field=models.DateTimeField(default='2023-11-17 22:24:49.415654'),
        ),
    ]
