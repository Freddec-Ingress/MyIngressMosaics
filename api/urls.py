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
	
	url(r'^mosaic/edit/',			MosaicViewSet.as_view({ 'post'  : 'edit'   })),
	url(r'^mosaic/reorder/',			MosaicViewSet.as_view({ 'post'  : 'reorder'   })),
	url(r'^mosaic/remove/',			MosaicViewSet.as_view({ 'post'  : 'remove'   })),
	url(r'^mosaic/add/',			MosaicViewSet.as_view({ 'post'  : 'add'   })),
	url(r'^mosaic/delete/',			MosaicViewSet.as_view({ 'post'  : 'delete'   })),
	url(r'^mosaic/potential/',			MosaicViewSet.as_view({ 'post'  : 'potential'   })),
	url(r'^mosaic/create/',	ProfileViewSet.as_view({ 'post' : 'create' })),
	url(r'^mosaic/(?P<ref>\w+)/$',	MosaicViewSet.as_view({ 'get'  : 'view'   })),
	
	url(r'^profile/name/',	ProfileViewSet.as_view({ 'post': 'name'     })),
	url(r'^profile/',		ProfileViewSet.as_view({ 'get' : 'view'     })),
	url(r'^mission/delete/',		ProfileViewSet.as_view({ 'post' : 'deleteMission' })),
	url(r'^missions/',		ProfileViewSet.as_view({ 'get' : 'missions' })),
	url(r'^mosaics/',		ProfileViewSet.as_view({ 'get' : 'mosaics' })),

	url(r'^city/setRegion/',		DataViewSet.as_view({ 'post' : 'setRegion'		})),
	url(r'^city/rename/',		DataViewSet.as_view({ 'post' : 'renameCity'		})),
	url(r'^city/',		DataViewSet.as_view({ 'post' : 'city'		})),
	url(r'^world/',		DataViewSet.as_view({ 'post' : 'world'		})),
	url(r'^region/',	DataViewSet.as_view({ 'post' : 'region' 	})),
	url(r'^country/rename/',	DataViewSet.as_view({ 'post' : 'renameCountry'	})),
	url(r'^country/',	DataViewSet.as_view({ 'post' : 'country'	})),
	url(r'^creator/',	DataViewSet.as_view({ 'post' : 'creator'	})),
	url(r'^search/',	DataViewSet.as_view({ 'post' : 'search'		})),
]
