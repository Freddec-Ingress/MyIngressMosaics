#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .notif import *
from .views import *
from .im import *
from .adm import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_register/',			ext_registerMission),
	url(r'^ext_check/',				ext_isMissionRegistered),
	url(r'^ext_bounds/',			ext_checkBounds),
	
	url(r'^user/google/',			user_google),
	url(r'^user/edit/',				user_edit),
	url(r'^user/logout/',			user_logout),
	url(r'^user/details/',			user_getDetails),

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
	
	url(r'^mission/update/',		mission_update),
	url(r'^mission/details/',		mission_details),
	url(r'^mission/delete/',		mission_delete),
	url(r'^mission/order/',			mission_order),
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
	url(r'^city/teleport/',			city_teleport),

	url(r'^world/',					data_getMosaicsByCountry),
	url(r'^country/(?P<name>[\w|\W \(\)\-,.\']+)/$',				data_getMosaicsByRegion),
	url(r'^region/(?P<country>[\w|\W \(\)\-,.\']+)/(?P<name>[\w \-,.\']+)/$',				data_getMosaicsByCity),
	url(r'^new_region/(?P<country_name>[\w|\W \(\)\-,.\']+)/(?P<region_name>[\w \-,.\']+)/$',				newdata_getMosaicsByCity),
	url(r'^city/(?P<country>[\w|\W \(\)\-,.\']+)/(?P<region>[\w \-,.\']+)/(?P<name>[\w \-,.\']+)/$',				data_getMosaicsOfCity),
	url(r'^creator/(?P<name>[\w|\W \(\)\-,.\']+)/$',				data_getMosaicsByCreator),
	
	url(r'^map/mosaic/',			map_getMosaicOverview),
	url(r'^map/',					map_getMosaics),

	url(r'^comment/add/',			comment_add),
	url(r'^comment/update/',		comment_update),
	url(r'^comment/delete/',		comment_delete),

	url(r'^potentials/',				potential_getAll),
	url(r'^potential/detect/',			potential_detect),
	url(r'^potential/rename/',			potential_rename),
	url(r'^potential/deletetitle/',		potential_delete_title),
	url(r'^potential/delete/',			potential_delete),
	url(r'^potential/exclude/',			potential_exclude),
	url(r'^potential/validate/',		potential_validate),

	url(r'^adm/compare',					adm_compare),
	url(r'^adm/city/rename',				adm_renameCity),
	url(r'^adm/region/rename',				adm_renameRegion),

	url(r'^telegram/539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0', telegram_updates),
	
	url(r'^notif/create', notif_create),
	url(r'^notif/delete', notif_delete),
	
	url(r'^im/country', im_country),
	url(r'^im/region', im_region),
	url(r'^im/city', im_city),
	
	url(r'^im/mosaic/edit', im_mosaic_edit),
	url(r'^im/mosaic', im_mosaic),
]
