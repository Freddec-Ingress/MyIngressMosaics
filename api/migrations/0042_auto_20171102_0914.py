# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-02 09:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0041_mission_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='registerer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='missions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mosaic',
            name='tags',
            field=models.TextField(blank=True, null=True),
        ),
    ]
