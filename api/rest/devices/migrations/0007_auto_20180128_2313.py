# Generated by Django 2.0.1 on 2018-01-28 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_auto_20180128_0614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='uid',
            field=models.CharField(default='e0a54b1f-9710-4024-8eeb-ec42b9f051cf', max_length=40, unique=True),
        ),
    ]
