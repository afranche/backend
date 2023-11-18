# Generated by Django 4.2.6 on 2023-11-18 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_customised',
        ),
        migrations.AddField(
            model_name='product',
            name='is_customized',
            field=models.BooleanField(default=False, verbose_name='Is customized'),
        ),
        migrations.AlterField(
            model_name='product',
            name='characteristics',
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Product Characteristics'),
        ),
    ]
