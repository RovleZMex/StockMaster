# Generated by Django 4.2.5 on 2023-10-23 04:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0002_outputorder_worker_outputorderitem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='outputorder',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
