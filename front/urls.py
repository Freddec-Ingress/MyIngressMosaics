#!/usr/bin/env python
# coding: utf-8

from django.http import HttpResponse
from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap

from front import views



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^robots.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /admin/\nDisallow: /api/', content_type='text/plain')),
	url(r'^sitemap.xml$', views.sitemap),

	url(r'^mosaic/(?P<ref>\w+)', views.mosaic),
	
	url(r'^registration/(?P<searchstring>[^/]+)', views.registration),
	url(r'^registration', views.registration),
	
	url(r'^search/(?P<searchstring>[\w \-,]+)',	views.search),
	url(r'^search', views.search),
	
	url(r'^profile', views.profile),
	
	url(r'^map/(?P<location_name>[\w \-,]+)', views.map),
	url(r'^map', views.map),
	
	url(r'^world/(?P<country_name>[\w|\W \(\)\-,.\']+)/(?P<region_name>[\w|\W \-,.\']+)/(?P<city_name>[\w|\W \-,.\']+)', views.city),
	url(r'^world/(?P<country_name>[\w|\W \(\)\-,.\']+)/(?P<region_name>[\w|\W \-,.\']+)', views.region),
	url(r'^world/(?P<country_name>[\w|\W \(\)\-,.\']+)', views.country),
	url(r'^world', views.world),
	
	url(r'^creator/(?P<creator_name>[\w \-,.\']+)', views.creator),
	
	url(r'^.*', views.world),
]
