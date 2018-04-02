# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-02 11:49
from __future__ import unicode_literals

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0070_auto_20180328_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaic',
            name='mission_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='waiting',
            name='ref',
            field=models.CharField(default=api.models._createRef, max_length=32, unique=True),
        ),
    ]
