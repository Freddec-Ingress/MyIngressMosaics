#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .views import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_check/',		ext_check),
	url(r'^ext_register/',	ExtensionViewSet.as_view({ 'post': 'register'	})),
	
	url(r'^login/',		AccountViewSet.as_view({ 'post': 'login'    })),
	url(r'^logout/',	AccountViewSet.as_view({ 'post': 'logout'   })),
	url(r'^register/',	AccountViewSet.as_view({ 'post': 'register' })),
	
	url(r'^profile/name/',	ProfileViewSet.as_view({ 'post': 'name'     })),
	url(r'^profile/',		ProfileViewSet.as_view({ 'get' : 'view'     })),
	url(r'^mission/delete/',		ProfileViewSet.as_view({ 'post' : 'deleteMission' })),
	url(r'^missions/',		ProfileViewSet.as_view({ 'get' : 'missions' })),
	url(r'^mosaics/',		ProfileViewSet.as_view({ 'get' : 'mosaics' })),
	url(r'^mosaic/create/',	ProfileViewSet.as_view({ 'post' : 'create' })),
	
	url(r'^mosaic/name/',			MosaicViewSet.as_view({ 'post'  : 'name'   })),
	url(r'^mosaic/(?P<ref>\w+)/$',	MosaicViewSet.as_view({ 'get'  : 'view'   })),
]
