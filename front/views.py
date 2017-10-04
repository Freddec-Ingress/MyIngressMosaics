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



def sitemap(request):

	text = ''
	text += '<?xml version="1.0" encoding="UTF-8"?>'
	text += '<urlset'
	text += '	xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
	text += '	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
	text += '	xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">'
    
    # Static URLs
    
	text += '<url><loc>https://www.myingressmosaics.com</loc><changefreq>daily</changefreq></url>'
	text += '<url><loc>https://www.myingressmosaics.com/map</loc><changefreq>daily</changefreq></url>'
	text += '<url><loc>https://www.myingressmosaics.com/search</loc><changefreq>daily</changefreq></url>'
    
    # Mosaic URLs
    
	mosaics = Mosaic.objects.all()
	for mosaic in mosaics:
		text += '<url><loc>https://www.myingressmosaics.com/mosaic/' + mosaic.ref + '</loc><changefreq>monthly</changefreq></url>'
     
	# Country URLs
	
	countries = Mosaic.objects.values('country').distinct()
	for country in countries:
		text += '<url><loc>https://www.myingressmosaics.com/map/' + country['country'] + '</loc><changefreq>daily</changefreq></url>'

	text += '</urlset>'
    
	response = HttpResponse(text, content_type = 'text/plain')
	return response



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
	
	imgByteArr = io.BytesIO()
	image.save(imgByteArr, format='PNG')
	imgByteArr = imgByteArr.getvalue()

	from django.core.files.storage import default_storage
	name = ''+ref+'.png'
	file = default_storage.open(name, 'w')
	file.write(imgByteArr)
	file.close()

	return response



def mosaic(request, ref):
	
	mosaic = None
	
	results = Mosaic.objects.filter(ref=ref)
	if (results.count() > 0):
		mosaic = results[0]
	
	if (mosaic):
		
		desc = mosaic.country
		if mosaic.region:
			desc += ' > ' + mosaic.region
		if mosaic.city:
			desc += ' > ' + mosaic.city
		desc += ' - ' + str(len(mosaic.missions.all())) + ' missions' + ' - ' + mosaic.type
	
		mcount = mosaic.missions.count()
		
		mosaic_rows = int(math.ceil(mcount / mosaic.cols))
		
		img_height = 32 + 20 + (100 * mosaic_rows)
		if (img_height < 352):
			img_height = 352
		
		context = { 'ref': ref, 'name': mosaic.title, 'desc': desc, 'img_height': img_height }
		
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

	
	
def adm_registration(request):
	
	context = {}
	return render(request, 'adm_registration.html', context)



def city(request, country, region, city):
	
	context = { 'country':country, 'region':region, 'city':city }
	return render(request, 'city.html', context)



def region(request, country, region):
	
	context = { 'country':country, 'region':region }
	return render(request, 'region.html', context)



def country(request, country):
	
	context = { 'country':country }
	return render(request, 'country.html', context)



def world(request):
	
	context = {}
	return render(request, 'world.html', context)
