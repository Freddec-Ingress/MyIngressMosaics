#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .views import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_register/',			ext_registerMission),
	url(r'^ext_check/',				ext_isMissionRegistered),
	url(r'^ext_bounds/',			ext_checkBounds),
	
	url(r'^user/google/',			user_google),
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
	url(r'^mosaic/link/',			mosaic_link),
	url(r'^mosaic/unlink/',			mosaic_unlink),
	url(r'^mosaic/love/',			mosaic_love),
	url(r'^mosaic/unlove/',			mosaic_unlove),
	url(r'^mosaic/complete/',		mosaic_complete),
	url(r'^mosaic/uncomplete/',		mosaic_uncomplete),
	url(r'^mosaic/(?P<ref>\w+)/$',	mosaic_view),
	
	url(r'^mission/delete/',		mission_delete),
	url(r'^mission/order/',			mission_order),
	url(r'^mission/exclude/',		mission_exclude),
	url(r'^missions/byname/',		data_missionsByName),

	url(r'^new_missions/',			data_newSearchForMissions),
	url(r'^missions/',				data_searchForMissions),
	url(r'^search/',				data_searchForMosaics),
	
	url(r'^country/list/',			country_getList),
	url(r'^country/create/',		country_create),
	url(r'^country/update/',		country_update),
	
	url(r'^region/list/',			region_getListFromCountry),
	url(r'^region/create/',			region_create),
	url(r'^region/update/',			region_update),
	url(r'^region/move/',			region_move),
	url(r'^region/delete/',			region_delete),
	
	url(r'^city/list/',				city_getListFromCountryRegion),
	url(r'^city/create/',			city_create),
	url(r'^city/update/',			city_update),
	url(r'^city/move/',				city_move),
	url(r'^city/delete/',			city_delete),

	url(r'^world/',					data_getMosaicsByCountry),
	url(r'^country/(?P<name>[\w \-,.\']+)/$',				data_getMosaicsByRegion),
	url(r'^region/(?P<country>[\w \-,.\']+)/(?P<name>[\w \-,.\']+)/$',				data_getMosaicsByCity),
	url(r'^new_region/(?P<country_name>[\w \-,.\']+)/(?P<region_name>[\w \-,.\']+)/$',				newdata_getMosaicsByCity),
	url(r'^city/(?P<country>[\w \-,.\']+)/(?P<region>[\w \-,.\']+)/(?P<name>[\w \-,.\']+)/$',				data_getMosaicsOfCity),
	url(r'^creator/(?P<name>[\w \-,.\']+)/$',				data_getMosaicsByCreator),
	
	url(r'^map/mosaic/',			map_getMosaicOverview),
	url(r'^map/',					map_getMosaics),

	url(r'^comment/add/',			comment_add),
	url(r'^comment/update/',		comment_update),
	url(r'^comment/delete/',		comment_delete),
	
	url(r'^potentials/tovalidate/',		data_getPotentialsToValidate),
	url(r'^potentials/',		data_getPotentials),
	url(r'^potential/name/',		data_getPotentialMissionByName),

	url(r'^opportunities/',		data_getOpportunities),
	
	url(r'^adm/city/rename',				adm_renameCity),
	url(r'^adm/region/rename',				adm_renameRegion),
	url(r'^adm/potential/exclude',				adm_excludePotential),
	url(r'^adm/potential/validate',				adm_validatePotential),

	url(r'^event/',				event_view),
]
