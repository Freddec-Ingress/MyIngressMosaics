#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .views import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_register/',			ext_registerMission),
	url(r'^ext_check/',				ext_isMissionRegistered),
	url(r'^ext_bounds/',			ext_checkBounds),
	
	url(r'^user/edit/',				user_edit),
	url(r'^user/register/',			user_register),
	url(r'^user/logout/',			user_logout),
	url(r'^user/login/',			user_login),
	url(r'^user/details/',			user_getDetails),
	url(r'^user/',					user_getProfile),
	
	url(r'^mosaic/missions/',		mosaic_searchForMissions),
	url(r'^mosaic/reorder/',		mosaic_reorder),
	url(r'^mosaic/delete/',			mosaic_delete),
	url(r'^mosaic/create/',			mosaic_create),
	url(r'^mosaic/remove/',			mosaic_removeMission),
	url(r'^mosaic/edit/',			mosaic_edit),
	url(r'^mosaic/add/',			mosaic_addMission),
	url(r'^mosaic/love/',			mosaic_love),
	url(r'^mosaic/unlove/',			mosaic_unlove),
	url(r'^mosaic/complete/',		mosaic_complete),
	url(r'^mosaic/uncomplete/',		mosaic_uncomplete),
	url(r'^mosaic/(?P<ref>\w+)/$',	mosaic_view),
	
	url(r'^mission/delete/',		mission_delete),
	url(r'^mission/order/',			mission_order),
	url(r'^mission/exclude/',		mission_exclude),

	url(r'^missions/',				data_searchForMissions),
	url(r'^search/',				data_searchForMosaics),

	url(r'^world/',					data_getMosaicsByCountry),
	url(r'^country/(?P<name>[\w \-,\']+)/$',				data_getMosaicsByRegion),
	url(r'^region/(?P<country>[\w \-,\']+)/(?P<name>[\w \-,\']+)/$',				data_getMosaicsByCity),
	url(r'^city/(?P<country>[\w \-,\']+)/(?P<region>[\w \-,\']+)/(?P<name>[\w \-,\']+)/$',				data_getMosaicsOfCity),
	
	url(r'^map/mosaic/',			map_getMosaicOverview),
	url(r'^map/',					map_getMosaics),

	url(r'^comment/add/',			comment_add),
	url(r'^comment/update/',		comment_update),
	url(r'^comment/delete/',		comment_delete),
	
	url(r'^potentials/',		data_getPotentials),
	url(r'^potential/name/',		data_getPotentialMissionByName),

	url(r'^opportunities/',		data_getOpportunities),
	
	url(r'^adm/city/rename',				adm_renameCity),
	url(r'^adm/region/rename',				adm_renameRegion),
	url(r'^adm/potential/exclude',				adm_excludePotential),

	url(r'^event/',				event_view),
]
