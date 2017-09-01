from django.shortcuts import render

from api.models import *

from PIL import Image, ImageDraw

from django.http import HttpResponse

import math
import urllib, io

from operator import itemgetter, attrgetter, methodcaller

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



def preview(request, ref):

	mosaic = Mosaic.objects.get(ref=ref)
	
	mosaic_rows = int(math.ceil(mosaic.missions.count() / mosaic.cols)) + 1
	
	img_height = 32 + 20 + (100 * mosaic_rows)
	if (img_height < 253):
		img_height = 253
	
	image = Image.new('RGBA', (632, img_height), (0, 77, 64))

	draw = ImageDraw.Draw(image)
	draw.rectangle(((8, 8), (624, img_height - 52 + 16)), fill = 'black')
	
	mcount = mosaic.missions.count()

	realx = mosaic.cols * 100
	realy = mosaic_rows * 100
	
	paddingX = 16 + (600 - realx) / 2
	paddingY = 16

	for m in mosaic.missions.all():

		file = io.BytesIO(urllib.request.urlopen(m.image + '=s100').read())
		mimg = Image.open(file)
		
		order = m.order - 1
		
		y = int(order / mosaic.cols)
		x = y + ((order + 1) - (y * mosaic.cols))
		
		xoffset = paddingX + (x * 100)
		yoffset = paddingY + (y * 100)
		
		image.paste(mimg, (int(xoffset), int(yoffset)));

	response = HttpResponse(content_type = 'image/png')
	image.save(response, 'PNG')
	return response



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
	
	
