#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import *

import cloudinary
import cloudinary.uploader



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_create(request):
	
	results = Country.objects.filter(name=request.data['country'])
	if results.count() > 0:
		country_obj = results[0]
	else:
		country_obj = Country(name=request.data['country'])
		country_obj.save()
		
	results = Region.objects.filter(country=country_obj, name=request.data['region'])
	if results.count() > 0:
		region_obj = results[0]
	else:
		region_obj = Region(country=country_obj, name=request.data['region'])
		region_obj.save()
		
	results = City.objects.filter(region=region_obj, name=request.data['city'])
	if results.count() > 0:
		city_obj = results[0]
	else:
		city_obj = City(region=region_obj, name=request.data['city'])
		city_obj.save()
		
	mosaic_obj = Mosaic(registerer=request.user, column_count=int(request.data['columns']), city=city_obj, title=request.data['title'])
	mosaic_obj.save()
	
	for item in request.data['missions']:
		mission_obj = Mission.objects.get(ref=item['ref'])
		mission_obj.mosaic = mosaic_obj
		mission_obj.order = item['order']
		mission_obj.save()
	
	mosaic_obj.computeInternalData()
	
	results = Potential.objects.filter(title=request.data['title'], city=city_obj)
	if results.count() > 0:
		results[0].delete()
	
	global maskimg_100
	if not maskimg_100:
		maskfile = io.BytesIO(urllib.request.urlopen('https://www.myingressmosaics.com/static/img/mask.png').read())
		maskimg_100 = Image.open(maskfile)
		size = 100, 100
		maskimg_100.thumbnail(size, Image.ANTIALIAS)
	
	global maskimg_25
	if not maskimg_25:
		maskfile = io.BytesIO(urllib.request.urlopen('https://www.myingressmosaics.com/static/img/mask.png').read())
		maskimg_25 = Image.open(maskfile)
		size = 25, 25
		maskimg_25.thumbnail(size, Image.ANTIALIAS)
			
	imgByteArr = mosaic_obj.generatePreview(100, maskimg_100)
	response = cloudinary.uploader.upload(imgByteArr, public_id=mosaic_obj.ref + '_100')
	mosaic_obj.big_preview_url = response['url']
	mosaic_obj.save()
	
	imgByteArr = mosaic_obj.generatePreview(25, maskimg_25)
	response = cloudinary.uploader.upload(imgByteArr, public_id=mosaic_obj.ref + '_25')
	mosaic_obj.small_preview_url = response['url']
	mosaic_obj.save()
	
	country_notifiers = Notif.objects.filter(country=country_obj, region__isnull=True, city__isnull=True).values_list('user__email')
	region_notifiers = Notif.objects.filter(country=country_obj, region=region_obj, city__isnull=True).values_list('user__email')
	city_notifiers = Notif.objects.filter(country=country_obj, region=region_obj, city=city_obj).values_list('user__email')
	
	receivers = []
	for item in country_notifiers: receivers.append(item[0])
	for item in region_notifiers: receivers.append(item[0])
	for item in city_notifiers: receivers.append(item[0])
	receivers = set(receivers)
	receivers = list(receivers)

	if len(receivers) > 0:
		
		msg_plain = render_to_string('new_mosaic.txt', { 'ref':mosaic_obj.ref, 'name':mosaic_obj.title, 'count':mosaic_obj.missions.all().count(), 'country':country_obj.name, 'region':region_obj.name, 'city':city_obj.name })
		
		for receiver in receivers:
			send_mail(
				'[MIM] New Mosaic Registered - ' + mosaic_obj.title,
		    	msg_plain,
		    	'admin@myingressmosaics.com',
		    	[receiver],
		    	fail_silently=False,
		    )
	
	return Response(mosaic_obj.ref, status=status.HTTP_200_OK)
