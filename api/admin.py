#!/usr/bin/env python
# coding: utf-8

from django.contrib import admin

from .models import *



#---------------------------------------------------------------------------------------------------
class MissionAdmin(admin.ModelAdmin):

	search_fields = ('title', 'creator', 'mosaic__title', )
	raw_id_fields = ('mosaic', )



#---------------------------------------------------------------------------------------------------
admin.site.register(Profile)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(Mosaic)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Comment)
admin.site.register(Search)
admin.site.register(Link)
admin.site.register(Potential)
admin.site.register(Notif)

admin.site.register(IMCountry)
admin.site.register(IMRegion)
admin.site.register(IMCity)
