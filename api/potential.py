#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_update(request):
	
	results = Mission.objects.filter(ref__in=request.data['refs'])
	for mission_obj in results:
		
		mission_obj.name = request.data['new_name']
		mission_obj.save()
		
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_exclude(request):
	
	results = Mission.objects.filter(ref__in=request.data['refs'])
	for mission_obj in results:
		
		mission_obj.admin = False
		mission_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_create(request):
	
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
		
	potential_obj = Potential(title=request.data['title'], mission_count=len(request.data['refs']), city=city_obj, country=country_obj)
	potential_obj.save()
	
	results = Mission.objects.filter(ref__in=request.data['refs'])
	for mission_obj in results:

		mission_obj.name = request.data['title']
		mission_obj.validated = True
		mission_obj.save()
	
	city_notifiers = Notif.objects.filter(country=country_obj, region=region_obj, city=city_obj).values_list('user__email')
	region_notifiers = Notif.objects.filter(country=country_obj, region=region_obj, city__isnull=True).values_list('user__email')
	country_notifiers = Notif.objects.filter(country=country_obj, region__isnull=True, city__isnull=True).values_list('user__email')
	
	receivers = []
	for item in country_notifiers: receivers.append(item[0])
	for item in region_notifiers: receivers.append(item[0])
	for item in city_notifiers: receivers.append(item[0])
	receivers = set(receivers)
	receivers = list(receivers)

	if len(receivers) > 0:
		
		msg_plain = render_to_string('new_potential.txt', { 'url':potential_obj.title.replace(' ', '%20'), 'name':potential_obj.title, 'count':potential_obj.mission_count, 'country':country_obj.name, 'region':region_obj.name, 'city':city_obj.name })
		
		for receiver in receivers:
			send_mail(
				'[MIM] New Potential Detected - ' + potential_obj.title,
		    	msg_plain,
		    	'admin@myingressmosaics.com',
		    	[receiver],
		    	fail_silently=False,
		    )

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_delete(request):

	results = Potential.objects.filter(title=request.data['title'], city__name=request.data['city_name'], country__name=request.data['country_name'])
	if results.count() > 0:
		potential_obj = results[0]
		potential_obj.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_refresh(request):
	
	data = {
		
		'missions':[],
	}
	
	results = Mission.objects.filter(name__icontains=request.data['text'], mosaic__isnull=True, admin=True, validated=False)
	for mission_obj in results:
		
		mission_data = {
			
			'ref':mission_obj.ref,
			'title':mission_obj.title,
			'image':mission_obj.image,
			'creator':mission_obj.creator,
			
			'startLat':mission_obj.startLat,
			'startLng':mission_obj.startLng,
		}
		
		data['missions'].append(mission_data)
	
	return Response(data, status=status.HTTP_200_OK)
	