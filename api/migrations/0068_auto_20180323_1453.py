# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-23 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0067_auto_20180323_1033'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mosaic',
            old_name='cols',
            new_name='column_count',
        ),
        migrations.AddField(
            model_name='mosaic',
            name='waypoint_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
