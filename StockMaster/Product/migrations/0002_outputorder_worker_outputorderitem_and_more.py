# Generated by Django 4.2.5 on 2023-10-22 22:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutputOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('workerCode', models.PositiveIntegerField()),
                ('zone', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OutputOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('outputOrder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Product.outputorder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.product')),
            ],
        ),
        migrations.AddField(
            model_name='outputorder',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.worker'),
        ),
    ]
