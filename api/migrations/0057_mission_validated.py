# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-16 18:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0056_country_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='validated',
            field=models.BooleanField(default=False),
        ),
    ]