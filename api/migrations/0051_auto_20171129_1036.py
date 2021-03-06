# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-29 10:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_auto_20171127_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cities', to='api.Region'),
        ),
        migrations.AlterField(
            model_name='mosaic',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mosaics', to='api.City'),
        ),
        migrations.AlterField(
            model_name='region',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='regions', to='api.Country'),
        ),
    ]
