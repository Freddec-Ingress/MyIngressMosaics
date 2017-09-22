# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-22 08:22
from __future__ import unicode_literals

from django.db import migrations, models

from api.models import *



def update(apps, schema_editor):
    
    mosaics = Mosaic.objects.all()
    for m in mosaics:
        
        m.creators = ''
        
        for item in m.missions.all().order_by('order'):
            
            if item.creator not in m.creators:
                m.creators += '|' + item.creator + '|'

        m.save()



class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_auto_20170921_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaic',
            name='creators',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.RunPython(update),
    ]
