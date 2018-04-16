#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import *

import cloudinary
import cloudinary.uploader

from urllib.request import Request



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_create(request):
	
	results = Country.objects.filter(Q(name__iexact=request.data['country']) | Q(locale__iexact=request.data['country']))
	if results.count() > 0:
		country_obj = results[0]
	else:
		country_obj = Country(name=request.data['country'])
		country_obj.save()
		
	results = Region.objects.filter(country=country_obj).filter(Q(name__iexact=request.data['region']) | Q(locale__iexact=request.data['region']))
	if results.count() > 0:
		region_obj = results[0]
	else:
		region_obj = Region(country=country_obj, name=request.data['region'])
		region_obj.save()
		
	results = City.objects.filter(region=region_obj).filter(Q(name__iexact=request.data['city']) | Q(locale__iexact=request.data['city']))
	if results.count() > 0:
		city_obj = results[0]
	else:
		city_obj = City(region=region_obj, name=request.data['city'])
		city_obj.save()
		
	mosaic_obj = Mosaic(registerer=request.user, column_count=int(request.data['columns']), city=city_obj, title=request.data['title'])
	
	if request.data['tags']:
		mosaic_obj.tags = request.data['tags']
	
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
	
	imgByteArr = mosaic_obj.generatePreview(25)
	if imgByteArr:
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



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_preview_generate(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	
	imgByteArr = mosaic_obj.generatePreview(25)
	if imgByteArr:
		response = cloudinary.uploader.upload(imgByteArr, public_id=mosaic_obj.ref + '_25')
		mosaic_obj.small_preview_url = response['url']
		mosaic_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_compute(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	mosaic_obj.computeInternalData()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_addtag(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if not mosaic_obj.tags: mosaic_obj.tags = ''
	mosaic_obj.tags += request.data['tag'] + '|'
	mosaic_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_rename(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators): 

		mosaic_obj.title = 	request.data['newname']
		mosaic_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_move(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators): 

		results = Country.objects.filter(Q(name__iexact=request.data['country_name']) | Q(locale__iexact=request.data['country_name']))
		if results.count() > 0:
			country_obj = results[0]
		else:
			country_obj = Country(name=request.data['country_name'])
			country_obj.save()
			
		results = Region.objects.filter(country=country_obj).filter(Q(name__iexact=request.data['region_name']) | Q(locale__iexact=request.data['region_name']))
		if results.count() > 0:
			region_obj = results[0]
		else:
			region_obj = Region(country=country_obj, name=request.data['region_name'])
			region_obj.save()
			
		results = City.objects.filter(region=region_obj).filter(Q(name__iexact=request.data['city_name']) | Q(locale__iexact=request.data['city_name']))
		if results.count() > 0:
			city_obj = results[0]
		else:
			city_obj = City(region=region_obj, name=request.data['city_name'])
			city_obj.save()

		mosaic_obj.city = city_obj
		mosaic_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_reorder(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators): 

		mission_obj = Mission.objects.get(id=request.data['mission_id'], mosaic__ref=request.data['ref'])
		mission_obj.order = request.data['neworder']
		mission_obj.save()
		
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_addmission(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators): 

		mission_obj = Mission.objects.get(id=request.data['mission_id'], mosaic__isnull=True)
		mission_obj.mosaic = mosaic_obj
		mission_obj.order = request.data['order']
		mission_obj.save()
		
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_removemission(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators): 

		mission_obj = Mission.objects.get(id=request.data['mission_id'], mosaic__ref=request.data['ref'])
		mission_obj.mosaic = None
		mission_obj.order = 0
		mission_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_delete(request):

	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators): 

		mosaic_obj.delete()

	return Response(None, status=status.HTTP_200_OK)
