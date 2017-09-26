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
	
	url(r'^search',        views.search),
	url(r'^login',         views.login),
	url(r'^creator',       views.creator),
	url(r'^registration',  views.registration),
	url(r'^register', views.register),
	url(r'^profile', views.profile),
	url(r'^plugin', views.plugin),
	
	url(r'^adm_region', views.adm_region),
	url(r'^adm_registration', views.adm_registration),
	
	url(r'^.*', views.home, name='home'),
]
