# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-06 07:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_mission_validated'),
    ]

    operations = [
        migrations.CreateModel(
            name='Potential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('count', models.IntegerField()),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='potentials', to='api.City')),
            ],
        ),
    ]