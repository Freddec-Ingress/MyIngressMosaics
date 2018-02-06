# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-06 15:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0058_potential'),
    ]

    operations = [
        migrations.AddField(
            model_name='potential',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='potentials', to='api.Country'),
        ),
    ]
