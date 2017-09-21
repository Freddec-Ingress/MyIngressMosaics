# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-21 07:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20170921_0705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mosaic',
            name='_distance',
        ),
        migrations.RemoveField(
            model_name='mosaic',
            name='_startLat',
        ),
        migrations.RemoveField(
            model_name='mosaic',
            name='_startLng',
        ),
        migrations.RemoveField(
            model_name='mosaic',
            name='creators',
        ),
        migrations.AlterField(
            model_name='mosaic',
            name='cols',
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='mosaic',
            name='country',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='mosaic',
            name='type',
            field=models.CharField(default=b'sequence', max_length=64),
        ),
        migrations.DeleteModel(
            name='Creator',
        ),
    ]
