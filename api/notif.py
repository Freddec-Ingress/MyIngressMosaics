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
def notif_create(request):
	
	country_name = request.data['country_name']
	
	region_name = None
	if 'region_name' in request.data: region_name = request.data['region_name']
	
	city_name = None
	if 'city_name' in request.data: city_name = request.data['city_name']
	
	# Retrieve data
	
	city_obj = None
	region_obj = None
	country_obj = None
	
	if country_name:
		country_obj = Country.objects.get(name=country_name)
		
		if region_name:
			region_obj = Region.objects.get(country=country_obj, name=region_name)
	
			if city_name:
				city_obj = City.objects.get(region=region_obj, name=city_name)
			
	# Check if same notification already exists
	
	already_existing = False
	
	results = Notif.objects.filter(user=request.user, country=country_obj, region=region_obj, city=city_obj)
	if results.count() > 0:
		already_existing = True
	
	# Create new notification
	
	if not already_existing:
		
		notif_obj = Notif(user=request.user, country=country_obj, region=region_obj, city=city_obj)
		notif_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def notif_delete(request):
	
	country_name = request.data['country_name']
	
	region_name = None
	if 'region_name' in request.data: region_name = request.data['region_name']
	
	city_name = None
	if 'city_name' in request.data: city_name = request.data['city_name']

	# Retrieve data
	
	city_obj = None
	region_obj = None
	country_obj = None
	
	if country_name:
		country_obj = Country.objects.get(name=country_name)
		
		if region_name:
			region_obj = Region.objects.get(country=country_obj, name=region_name)
	
			if city_name:
				city_obj = City.objects.get(region=region_obj, name=city_name)
				
	# Delete existing notification
	
	notif_obj = Notif.objects.get(user=request.user, country=country_obj, region=region_obj, city=city_obj)
	notif_obj.delete()
	
	return Response(None, status=status.HTTP_200_OK)
