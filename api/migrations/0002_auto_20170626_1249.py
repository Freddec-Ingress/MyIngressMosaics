# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-26 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='ref',
            field=models.CharField(default=b'', max_length=128),
        ),
        migrations.AlterField(
            model_name='mission',
            name='data',
            field=models.CharField(max_length=2048),
        ),
    ]
