from django.shortcuts import render, redirect

from django.db.models import Q

from api.models import *

from PIL import Image, ImageDraw, ImageFont

from django.http import HttpResponse

import re
import math, os
import urllib, io

from operator import itemgetter, attrgetter, methodcaller

	
	
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
	text += '<url><loc>https://www.myingressmosaics.com/world</loc><changefreq>daily</changefreq></url>'
	text += '<url><loc>https://www.myingressmosaics.com/search</loc><changefreq>daily</changefreq></url>'
	text += '<url><loc>https://www.myingressmosaics.com/profile</loc><changefreq>daily</changefreq></url>'
	text += '<url><loc>https://www.myingressmosaics.com/registration</loc><changefreq>daily</changefreq></url>'
    
    # Mosaic URLs
    
	mosaics = Mosaic.objects.all()
	for mosaic in mosaics:
		text += '<url><loc>https://www.myingressmosaics.com/mosaic/' + mosaic.ref + '</loc><changefreq>monthly</changefreq></url>'
     
	# Country URLs
	
	countries = Country.objects.all()
	for country in countries:
		text += '<url><loc>https://www.myingressmosaics.com/world/' + country.name + '</loc><changefreq>daily</changefreq></url>'
     
	# Region URLs
	
	regions = Region.objects.all()
	for region in regions:
		text += '<url><loc>https://www.myingressmosaics.com/world/' + region.country.name + '/' + region.name + '</loc><changefreq>daily</changefreq></url>'
      
	# City URLs
	
	cities = City.objects.all()
	for city in cities:
		text += '<url><loc>https://www.myingressmosaics.com/world/' + city.region.country.name + '/' + city.region.name + '/' + city.name + '</loc><changefreq>daily</changefreq></url>'
       
	# Creator URLs
	
	creators = Mission.objects.order_by('creator').values('creator').distinct()
	for creator in creators:
		if creator['creator']:
			text += '<url><loc>https://www.myingressmosaics.com/creator/' + creator['creator'] + '/' + '</loc><changefreq>daily</changefreq></url>'
	
	text += '</urlset>'
    
	response = HttpResponse(text, content_type = 'text/plain')
	return response



def preview(request, ref):

	mosaic = Mosaic.objects.get(ref=ref)
	return redirect(mosaic.generatePreview())
	
	
	
def mosaic(request, ref):

	mosaic = None
	
	results = Mosaic.objects.filter(ref=ref)
	if (results.count() > 0):
		mosaic = results[0]
	
	if (mosaic):
		
		desc = mosaic.city.region.country.name
		if mosaic.city.region:
			desc += ' > ' + mosaic.city.region.name
		if mosaic.city:
			desc += ' > ' + mosaic.city.name
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
	
	
	
def registration(request, searchstring = ''):
	
	context = { 'searchstring':searchstring }
	return render(request, 'registration.html', context)
	
	
	
def search(request, searchstring = ''):
	
	context = { 'searchstring':searchstring }
	return render(request, 'search.html', context)

	
	
def profile(request):
	
	context = {}
	return render(request, 'profile.html', context)

	
	
def login(request):
	
	context = {}
	return render(request, 'login.html', context)
	
	
	
def register(request):
	
	context = {}
	return render(request, 'register.html', context)
	
	
	
def map(request, location = ''):
	
	context = {'location': location}
	return render(request, 'map.html', context)



def world(request):
	
	context = {}
	return render(request, 'world.html', context)



def city(request, country, region, city):
	
	context = { 'country_label':country, 'region_label':region, 'city_label':city, 'country_name':re.escape(country), 'region_name':re.escape(region), 'city_name':re.escape(city) }
	return render(request, 'city.html', context)



def region(request, country, region):
	
	context = { 'country':country, 'region':re.escape(region), 'regionlabel':region }
	return render(request, 'region.html', context)
	
	
	
def country(request, country):
	
	context = { 'country':country }
	return render(request, 'country.html', context)
	
	
	
def creator(request, name):
	
	context = { 'name':name }
	return render(request, 'creator.html', context)



def recruitment(request):
	
	context = {}
	return render(request, 'recruitment.html', context)



def adm_region(request):	
	
	context = {}
	return render(request, 'adm_region.html', context)



def adm_city(request):	
	
	context = {}
	return render(request, 'adm_city.html', context)



def adm_registration(request):	
	
	context = {}
	return render(request, 'adm_registration.html', context)
	


def adm_mosaic(request, ref):	
	
	context = { 'ref':ref }
	return render(request, 'adm_mosaic.html', context)