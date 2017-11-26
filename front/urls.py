from django.conf.urls import url

from django.http import HttpResponse

from django.contrib.sitemaps.views import sitemap

from front import views

urlpatterns = [
	
	url(r'^robots.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /admin/\nDisallow: /api/', content_type='text/plain')),
	url(r'^sitemap.xml$', views.sitemap),
    
	url(r'^map/(?P<location>[\w \-,]+)',           views.map),
	url(r'^map',           views.map),
	
	url(r'^mosaic/(?P<ref>\w+)/preview',        views.preview),
	url(r'^mosaic/(?P<ref>\w+)',        views.mosaic),
	
	url(r'^registration',  views.registration),
	
	url(r'^search/(?P<searchstring>[\w \-,]+)',           views.search),
	url(r'^search',        views.search),
	
	url(r'^events/(?P<eventstring>[\w \-,]+)',           views.events),
	url(r'^events',        views.events),
	
	url(r'^login',         views.login),
	url(r'^register', views.register),
	url(r'^profile', views.profile),

	url(r'^world/(?P<country>[\w \-,\']+)/(?P<region>[\w|\W \-,\']+)/(?P<city>[\w \-,\']+)', views.city),
	url(r'^world/(?P<country>[\w \-,\']+)/(?P<region>[\w|\W \-,\']+)', views.region),
	url(r'^world/(?P<country>[\w \-,\']+)', views.country),
	url(r'^world', views.world),
	
	url(r'^recruitment', views.recruitment),
	url(r'^migrate', views.migrate),
	
	
	
	url(r'^new_mosaic/(?P<ref>\w+)',				views.new_mosaic),
	
	url(r'^new_registration',						views.new_registration),
	
	url(r'^new_search/(?P<searchstring>[\w \-,]+)',	views.new_search),
	url(r'^new_search',     						views.new_search),
	
	url(r'^new_profile',							views.new_profile),
	
	url(r'^new_map/(?P<location>[\w \-,]+)',		views.new_map),
	url(r'^new_map',        						views.new_map),
	
	url(r'^new_login',      						views.new_login),
	
	url(r'^new_register',							views.new_register),
	
	url(r'^new_world/(?P<country>[\w \-,\']+)/(?P<region>[\w|\W \-,\']+)', views.new_region),
	url(r'^new_world/(?P<country>[\w \-,\']+)', 	views.new_country),
	url(r'^new_world',								views.new_world),
	
	url(r'^new_recruitment',						views.new_recruitment),
	
	url(r'^.*', 									views.world),
]
