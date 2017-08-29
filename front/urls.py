from django.conf.urls import url

from front import views

urlpatterns = [
	
	url(r'^map/(?P<location>[\w ]+)',           views.map),
	url(r'^map',           views.map),
	
	url(r'^mosaic/(?P<ref>\w+)',        views.mosaic),
	url(r'^search',        views.search),
	url(r'^login',         views.login),
	url(r'^creator',       views.creator),
	url(r'^registration',  views.registration),
	url(r'^register', views.register),
	url(r'^profile', views.profile),
	url(r'^plugin', views.plugin),
	
	url(r'^.*', views.home),
]
