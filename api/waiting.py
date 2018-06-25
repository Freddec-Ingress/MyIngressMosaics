#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def waiting_create(request):
	
	results = Country.objects.filter(name=request.data['country_name'])
	if results.count() > 0:
		country_obj = results[0]
	else:
		country_obj = Country(name=request.data['country_name'])
		country_obj.save()
		
	results = Region.objects.filter(country=country_obj, name=request.data['region_name'])
	if results.count() > 0:
		region_obj = results[0]
	else:
		region_obj = Region(country=country_obj, name=request.data['region_name'])
		region_obj.save()
		
	results = City.objects.filter(region=region_obj, name=request.data['city_name'])
	if results.count() > 0:
		city_obj = results[0]
	else:
		city_obj = City(region=region_obj, name=request.data['city_name'])
		city_obj.save()
	
	mission_refs = ''
	for data in request.data['missions']:
		
		mission_obj = Mission.objects.get(ref=data['ref'])

		mission_obj.admin = False
		mission_obj.order = data['order']
		mission_obj.name = request.data['title']
		mission_obj.save()
	
		mission_refs += '|' + item
	
	waiting_obj = Waiting(country=country_obj, region=region_obj, city=city_obj, title=request.data['title'], mission_refs=mission_refs, mission_count=request.data['mission_count'])
	waiting_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def waiting_delete(request):
	
	waiting_obj = Waiting.objects.get(ref=request.data['ref'])
	waiting_obj.delete()
	
	mission_refs = waiting_obj.mission_refs.split('|')
	for ref in mission_refs:
		if ref:
			
			mission_object = Mission.objects.get(ref=ref)
			mission_object.delete()
	
	return Response(None, status=status.HTTP_200_OK)
