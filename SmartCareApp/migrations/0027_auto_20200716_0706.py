# Generated by Django 3.0.3 on 2020-07-16 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartCareApp', '0026_logindetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='Behaviour',
            field=models.CharField(default='', max_length=50),
        ),
    ]
