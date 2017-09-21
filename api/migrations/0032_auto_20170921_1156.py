# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-21 11:56
from __future__ import unicode_literals

from django.db import migrations, models

from api.models import *



def rebuild(apps, schema_editor):
    
    missions = Mission.objects.all()
    for m in missions:
        m.computeInternalData();
    
    mosaics = Mosaic.objects.all()
    for m in mosaics:
        m.computeInternalData();



class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_auto_20170921_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='creator',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='desc',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='distance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='faction',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='image',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='startLat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mission',
            name='startLng',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mosaic',
            name='distance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mosaic',
            name='portals',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mosaic',
            name='startLat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mosaic',
            name='startLng',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mosaic',
            name='uniques',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='ref',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='mission',
            name='title',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        
        migrations.RunPython(rebuild),
    ]
