#!/usr/bin/env python
# coding: utf-8

from django.db import models

#---------------------------------------------------------------------------------------------------
class Mission(models.Model):

    data = models.CharField(max_length=2048)

    ref = models.CharField(max_length=128, default='')