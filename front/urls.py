#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url

from front import views



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^preview/(?P<ref>\w+)', views.preview),
	url(r'^mosaic/(?P<ref>\w+)', views.mosaic),
	url(r'^manage/(?P<ref>\w+)', views.manage),
	url(r'^waiting/(?P<ref>\w+)', views.waiting),

	url(r'^registration/(?P<search_string>[^/]+)', views.registration),
	url(r'^registration', views.registration),
	
	url(r'^tag/(?P<tag>[^/]+)', views.tag),
	
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
	
	url(r'^adm/im', views.adm_im),
	url(r'^adm/tag', views.adm_tag),
	url(r'^adm/city', views.adm_city),
	url(r'^adm/region', views.adm_region),
	url(r'^adm/compare', views.adm_compare),
	url(r'^adm/creators', views.adm_creators),
	url(r'^adm/missions', views.adm_missions),
	url(r'^adm/previews', views.adm_previews),
	
	url(r'^adm/potential/(?P<search_string>[^/]+)', views.adm_potential),
	url(r'^adm/potential', views.adm_potential),
	
	url(r'^.*', views.world),
]
