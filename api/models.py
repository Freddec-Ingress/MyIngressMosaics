#!/usr/bin/env python
# coding: utf-8

from django.db import models

#---------------------------------------------------------------------------------------------------
class Mission(models.Model):

    data = models.CharField(max_length=4096)

    ref = models.CharField(max_length=64, default='')
    desc = models.CharField(max_length=1024, default='')
    title = models.CharField(max_length=128, default='')
    image = models.CharField(max_length=256, default='')
    creator = models.CharField(max_length=32, default='')
    faction = models.CharField(max_length=8, default='')



#---------------------------------------------------------------------------------------------------
class Portal(models.Model):

    mission = models.ForeignKey('Mission', on_delete=models.CASCADE, null=True, blank=True)

    lat = models.FloatField(default=0.0)
    lng = models.FloatField(default=0.0)
    order = models.IntegerField(default=-1)
    title = models.CharField(max_length=128, default='')
