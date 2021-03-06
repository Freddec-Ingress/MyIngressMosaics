# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-16 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0063_auto_20180313_0856'),
    ]

    operations = [
        migrations.CreateModel(
            name='IMMosaic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=128)),
                ('region_name', models.CharField(max_length=128)),
                ('city_name', models.CharField(max_length=128)),
                ('compare_name', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('count', models.IntegerField()),
            ],
        ),
    ]
