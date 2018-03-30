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
from .waiting import *
from .comment import *
from .telegram import *
from .potential import *



#---------------------------------------------------------------------------------------------------
urlpatterns = [
	
	url(r'^ext_check/', ext_isMissionRegistered),
	url(r'^ext_bounds/', ext_checkBounds),
	url(r'^ext_register/', ext_registerMission),
	
	url(r'^user/edit/', user_edit),
	url(r'^user/google/', user_google),
	url(r'^user/logout/', user_logout),
	url(r'^user/redirect/', user_redirect),

	url(r'^mosaic/create/', mosaic_create),

	url(r'^link/create/', link_create),
	url(r'^link/delete/', link_delete),

	url(r'^search/missions/', search_missions),
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
	
	url(r'^im/city/', im_city),
	url(r'^im/region/', im_region),
	url(r'^im/country/', im_country),
	url(r'^im/mosaic/die/', im_mosaic_die),
	url(r'^im/mosaic/exclude/', im_mosaic_exclude),
	
	url(r'^waiting/create/', waiting_create),
]
