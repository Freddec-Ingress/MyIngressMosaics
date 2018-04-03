#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url

from front import views



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^preview/(?P<ref>\w+)', views.preview),
	url(r'^mosaic/(?P<ref>\w+)', views.mosaic),
	
	url(r'^registration/(?P<search_string>[^/]+)', views.registration),
	url(r'^registration', views.registration),
	
	url(r'^search/(?P<search_string>[^/]+)', views.search),
	url(r'^search', views.search),
	
	url(r'^profile', views.profile),
	
	url(r'^map/(?P<location_name>[\w \-,]+)', views.map),
	url(r'^map', views.map),
	
	url(r'^world/(?P<country_name>[\w|\W \(\)\-,.\']+)/(?P<region_name>[\w|\W \-,.\']+)/(?P<city_name>[\w|\W \-,.\']+)', views.city),
	url(r'^world/(?P<country_name>[\w|\W \(\)\-,.\']+)/(?P<region_name>[\w|\W \-,.\']+)', views.region),
	url(r'^world/(?P<country_name>[\w|\W \(\)\-,.\']+)', views.country),
	url(r'^world', views.world),
	
	url(r'^creator/(?P<creator_name>[\w \-,.\']+)', views.creator),
	
	url(r'^adm/checks', views.adm_checks),
	url(r'^adm/compare', views.adm_compare),
	url(r'^adm/registration', views.adm_registration),
	
	url(r'^.*', views.world),
]
