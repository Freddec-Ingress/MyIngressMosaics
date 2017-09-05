# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-05 07:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20170904_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_date', models.DateField(default=datetime.datetime.now)),
                ('search_text', models.CharField(default=b'', max_length=128)),
                ('count', models.IntegerField(default=-1)),
            ],
        ),
    ]
