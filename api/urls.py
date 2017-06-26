#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .views import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_check/',		ExtensionViewSet.as_view({ 'post': 'check'		})),
	url(r'^ext_register/',	ExtensionViewSet.as_view({ 'post': 'register'	})),
]
