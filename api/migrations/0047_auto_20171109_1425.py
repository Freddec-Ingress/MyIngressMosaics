# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-09 14:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0046_auto_20171109_1424'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mosaic',
            old_name='city_obj',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='mosaic',
            old_name='country_obj',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='mosaic',
            old_name='region_obj',
            new_name='region',
        ),
    ]
