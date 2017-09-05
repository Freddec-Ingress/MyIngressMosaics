#!/usr/bin/env python
# coding: utf-8

from django.contrib import admin

from .models import *



#---------------------------------------------------------------------------------------------------
admin.site.register(Profile)
admin.site.register(Creator)
admin.site.register(Mosaic)
admin.site.register(Mission)
admin.site.register(Portal)
admin.site.register(SearchResult)
