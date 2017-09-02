from django.shortcuts import render

from api.models import *

from PIL import Image, ImageDraw, ImageFont

from django.http import HttpResponse

import math, os
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
	
	mcount = mosaic.missions.count()
	
	mosaic_rows = int(math.ceil(mcount / mosaic.cols))
	
	img_height = 32 + 20 + (100 * mosaic_rows)
	if (img_height < 352):
		img_height = 352
	
	image = Image.new('RGBA', (632, img_height), (0, 77, 64))

	draw = ImageDraw.Draw(image)
	draw.rectangle(((8, 8), (624, img_height - 52 + 24)), fill = 'black')
	
	fontfile = io.BytesIO(urllib.request.urlopen('https://www.myingressmosaics.com/static/fonts/coda-regular.ttf').read())
	
	font = ImageFont.truetype(fontfile, 15)
	draw.text((16, img_height - 25), 'MIM - MyIngressMosaics.com', fill=(255, 255, 255), font=font)

	realx = 0
	if mcount < mosaic.cols:
		realx = mcount * 100
	else:
		realx = mosaic.cols * 100
	
	realy = mosaic_rows * 100
	
	paddingX = 16 + (600 - realx) / 2
	
	if mosaic_rows < 4:
		paddingY = 16 + (300 - realy) / 2
	else:
		paddingY = 16

	maskfile = io.BytesIO(urllib.request.urlopen('https://www.myingressmosaics.com/static/img/mask.png').read())
	maskimg = Image.open(maskfile)
		
	for m in mosaic.missions.all():

		file = io.BytesIO(urllib.request.urlopen(m.image + '=s100').read())
		mimg = Image.open(file)
		
		order = mcount - m.order
		
		y = int(order / mosaic.cols)
		x = int(order - (y * mosaic.cols))
		
		xoffset = paddingX + (x * 100)
		yoffset = paddingY + (y * 100)
		
		image.paste(mimg, (int(xoffset), int(yoffset)));
		image.paste(maskimg, (int(xoffset), int(yoffset)), maskimg);

	response = HttpResponse(content_type = 'image/png')
	image.save(response, 'PNG')
	return response



def mosaic(request, ref):
	
	mosaic = None
	
	results = Mosaic.objects.filter(ref=ref)
	if (results.count() > 0):
		mosaic = results[0]
	
	if (mosaic):
		
		portals = 0
		for m in mosaic.missions.all():
			portals += m.portals.all().count()
		
		desc = mosaic.country + ' > ' + mosaic.region + ' > ' + mosaic.city + ' \r\n ' + str(len(mosaic.missions.all())) + ' missions' + ' - ' + mosaic.type + ' - ' + str(portals) + ' portals'

		if (mosaic.type ==  'sequence'):
			desc += ' - ' + str(round(mosaic._distance, 2)) + ' km'
					
		context = { 'ref': ref, 'name': mosaic.title, 'desc': desc }
		
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
	
	
