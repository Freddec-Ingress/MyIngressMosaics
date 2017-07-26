from django.conf.urls import include, url

urlpatterns = [
	
	url(r'^map',           include('front.apps.map.urls')),
	url(r'^mosaic',        include('front.apps.mosaic.urls')),
	url(r'^search',        include('front.apps.search.urls')),
	url(r'^account',       include('front.apps.account.urls')),
	url(r'^creator',       include('front.apps.creator.urls')),
	url(r'^registration',  include('front.apps.registration.urls')),
	
	url(r'^.*', include('front.apps.home.urls')),
]
