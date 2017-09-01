from django.shortcuts import render

from api.models import *

def creator(request):
	
	context = {}
	return render(request, 'creator.html', context)
	
	
	
def home(request):
	
	context = {}
	return render(request, 'home.html', context)
	
	
	
def login(request):
	
	context = {}
	return render(request, 'login.html', context)
	
	
	
def map(request, location = ''):
	
	context = {'location': location}
	return render(request, 'map.html', context)



def mosaic(request, ref):
	
	mosaic = None
	
	results = Mosaic.objects.filter(ref=ref)
	if (results.count() > 0):
		mosaic = results[0]
	
	if (mosaic):
		context = { 'ref': ref, 'name': mosaic.title, 'desc': mosaic.country }
		
	else:
		context = { 'ref': ref }
		
	return render(request, 'mosaic.html', context)
	
	
	
def plugin(request):
	
	context = {}
	return render(request, 'plugin.html', context)
	
	
	
def profile(request):
	
	context = {}
	return render(request, 'profile.html', context)
	
	
	
def register(request):
	
	context = {}
	return render(request, 'register.html', context)
	
	
	
def registration(request):
	
	context = {}
	return render(request, 'registration.html', context)
	
	
	
def search(request):
	
	context = {}
	return render(request, 'search.html', context)
	
	
