# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-16 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_immosaic'),
    ]

    operations = [
        migrations.AddField(
            model_name='immosaic',
            name='dead',
            field=models.BooleanField(default=False),
        ),
    ]