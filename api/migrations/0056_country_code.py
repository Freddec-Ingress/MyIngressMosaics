# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-11 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='code',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
