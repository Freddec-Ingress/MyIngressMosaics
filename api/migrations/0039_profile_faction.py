# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-03 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_auto_20171002_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='faction',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
