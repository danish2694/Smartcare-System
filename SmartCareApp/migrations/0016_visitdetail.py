# Generated by Django 2.2 on 2019-07-31 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartCareApp', '0015_auto_20190729_0311'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Service_Order', models.CharField(max_length=10)),
                ('Location', models.CharField(max_length=10)),
                ('Technician', models.CharField(max_length=30)),
                ('Technician_Name', models.CharField(max_length=50)),
                ('Product_Code', models.CharField(max_length=10)),
                ('Serial_No', models.CharField(max_length=10)),
                ('Warranty', models.CharField(default='', max_length=10)),
                ('Contract_No', models.CharField(default='', max_length=50)),
                ('Visit_Date', models.CharField(max_length=10)),
                ('Start_Time', models.CharField(max_length=10)),
                ('End_Time', models.CharField(max_length=10)),
                ('Work_Done', models.CharField(max_length=10)),
                ('Action', models.CharField(max_length=10)),
                ('Remark', models.CharField(max_length=100)),
            ],
        ),
    ]