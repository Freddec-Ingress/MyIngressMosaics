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

	url(r'^world/(?P<country>[\w \-,\']+)/(?P<region>[\w \-,\']+)/(?P<city>[\w \-,\']+)', views.city),
	url(r'^world/(?P<country>[\w \-,\']+)/(?P<region>[\w \-,\']+)', views.region),
	url(r'^world/(?P<country>[\w \-,\']+)', views.country),
	url(r'^world', views.world),
	
	url(r'^.*', views.world),
]
