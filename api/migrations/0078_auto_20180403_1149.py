# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-02 11:49
from __future__ import unicode_literals

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0076_auto_20180403_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='desc',
            field=models.TextField(blank=True, null=True)
        ),
        migrations.AlterField(
            model_name='tag',
            name='tg_url',
            field=models.CharField(max_length=256, blank=True, null=True)
        ),
        migrations.AlterField(
            model_name='tag',
            name='gplus_url',
            field=models.CharField(max_length=256, blank=True, null=True)
        ),
    ]
