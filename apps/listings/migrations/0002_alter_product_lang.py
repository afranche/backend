# Generated by Django 4.2.6 on 2023-10-15 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='lang',
            field=models.CharField(choices=[], default='fr', max_length=3, verbose_name='Language'),
        ),
    ]