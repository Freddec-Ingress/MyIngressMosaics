#!/usr/bin/env python
# coding: utf-8

from django.contrib import admin

from .models import *



#---------------------------------------------------------------------------------------------------
admin.site.register(Profile)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(Mosaic)
admin.site.register(Mission)
admin.site.register(Comment)
admin.site.register(Search)
admin.site.register(Link)
admin.site.register(Potential)
admin.site.register(Notif)
