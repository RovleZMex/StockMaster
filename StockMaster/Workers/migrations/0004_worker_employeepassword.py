# Generated by Django 4.2.5 on 2023-11-14 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Workers', '0003_alter_worker_employeenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='employeePassword',
            field=models.CharField(default=123, max_length=255),
            preserve_default=False,
        ),
    ]
