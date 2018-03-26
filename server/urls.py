#!/usr/bin/env python
# coding: utf-8

from django.http import HttpResponse
from django.contrib import admin
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap

from front import views

urlpatterns = [

	url(r'^robots.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /admin/\nDisallow: /api/', content_type='text/plain')),
	url(r'^sitemap.xml$', views.sitemap),

	url(r'^api/', include('api.urls')),

    url(r'^admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    
	url(r'^', include('front.urls')),
)
