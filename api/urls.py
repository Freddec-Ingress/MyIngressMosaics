#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .views import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_portals/',	ExtensionViewSet.as_view({ 'post': 'portals'	})),
	url(r'^ext_missions/',	ExtensionViewSet.as_view({ 'post': 'missions'	})),
]
