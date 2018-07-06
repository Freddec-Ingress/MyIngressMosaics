#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import url, include

from .im import *
from .ext import *
from .map import *
from .user import *
from .link import *
from .notif import *
from .search import *
from .mosaic import *
from .mission import *
from .waiting import *
from .comment import *
from .location import *
from .telegram import *
from .potential import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_check/', ext_isMissionRegistered),
	url(r'^ext_bounds/', ext_checkBounds),
	url(r'^ext_register/', ext_registerMission),
	
	url(r'^user/editagentname/', user_editagentname),
	url(r'^user/edit/', user_edit),
	url(r'^user/google/', user_google),
	url(r'^user/logout/', user_logout),
	url(r'^user/redirect/', user_redirect),

	url(r'^mosaic/create/', mosaic_create),
	url(r'^mosaic/compute/', mosaic_compute),
	url(r'^mosaic/preview/generate/', mosaic_preview_generate),
	url(r'^mosaic/tag/add/', mosaic_addtag),
	url(r'^mosaic/rename/', mosaic_rename),
	url(r'^mosaic/move/', mosaic_move),
	url(r'^mosaic/reorder/', mosaic_reorder),
	url(r'^mosaic/addmission/', mosaic_addmission),
	url(r'^mosaic/removemission/', mosaic_removemission),
	url(r'^mosaic/delete/', mosaic_delete),
	url(r'^mosaic/obsolete/', mosaic_obsolete),
	url(r'^mosaic/ownermsg/', mosaic_ownermsg),
	
	url(r'^link/create/', link_create),
	url(r'^link/delete/', link_delete),

	url(r'^search/missions/', search_missions),
	url(r'^search/city/', search_city),
	url(r'^search/', search_mosaics),
	
	url(r'^map/', map_getMosaics),

	url(r'^comment/create/', comment_create),
	url(r'^comment/update/', comment_update),
	url(r'^comment/delete/', comment_delete),

	url(r'^potential/create/', potential_create),
	url(r'^potential/delete/', potential_delete),
	url(r'^potential/update/', potential_update),
	url(r'^potential/exclude/', potential_exclude),
	url(r'^potential/refresh/', potential_refresh),
	
	url(r'^telegram/539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0', telegram_updates),
	
	url(r'^notif/create/', notif_create),
	url(r'^notif/delete/', notif_delete),
	
	url(r'^mission/reorder/', mission_reorder),
	
	url(r'^im/city/', im_city),
	url(r'^im/region/', im_region),
	url(r'^im/country/', im_country),
	
	url(r'^im/mosaic/die/', im_mosaic_die),
	url(r'^im/mosaic/exclude/', im_mosaic_exclude),
	url(r'^im/mosaic/register/', im_mosaic_register),
	url(r'^im/mosaic/delete/', im_mosaic_delete),
	url(r'^im/mosaic/', im_mosaic),
	
	url(r'^waiting/update/', waiting_update),
	url(r'^waiting/create/', waiting_create),
	url(r'^waiting/delete/', waiting_delete),
	url(r'^waiting/deleteall/', waiting_deleteall),
	url(r'^waiting/addmission/', waiting_addmission),
	
	url(r'^location/city/list/', city_list),
	url(r'^location/city/merge/', city_merge),
	
	url(r'^location/region/list/', region_list),
	url(r'^location/region/merge/', region_merge),
	
	url(r'^location/country/list/', country_list),
]
