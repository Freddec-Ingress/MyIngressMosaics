from django.conf.urls import include, url

from django.contrib import admin

urlpatterns = [

	url(r'^api/', include('api.urls')),
	
	url(r'^login/', include('rest_social_auth.urls_token')),
	
    url(r'^admin/', admin.site.urls),
    
	url(r'^', include('front.urls')),
]