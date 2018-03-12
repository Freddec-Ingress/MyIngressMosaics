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
	region_name = request.data['region_name']
	city_name = request.data['city_name']
	
	# Retrieve data
	country_data = None
	region_data = None
	city_data = None
	
	if country_name:
		country_data = Country.objects.get(name=country_name)
		
		if region_name:
			region_data = Region.objects.get(country=country_data, name=region_name)
	
			if city_name:
				city_data = City.objects.get(country=country_data, region=region_data, name=city_name)
			
	# Check if same notification already exists
	already_existing = False
	
	results = Notif.objects.filter(user=request.user, country=country_data, region=region_data, city=city_data)
	if results.count() > 0:
		already_existing = True
	
	# Create new notification
	if not already_existing:
		
		new_notif = Notif(user=request.user, country=country_data, region=region_data, city=city_data)
		new_notif.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def notif_delete(request):
	
	country_name = request.data['country_name']
	region_name = request.data['region_name']
	city_name = request.data['city_name']

	# Retrieve data
	country_data = None
	region_data = None
	city_data = None
	
	if country_name:
		country_data = Country.objects.get(name=country_name)
		
		if region_name:
			region_data = Region.objects.get(country=country_data, name=region_name)
	
			if city_name:
				city_data = City.objects.get(country=country_data, region=region_data, name=city_name)
				
	# Delete existing notification
	results = Notif.objects.filter(user=request.user, country=country_data, region=region_data, city=city_data)
	if results.count() > 0:
		
		existing_notif = results[0]
		existing_notif.delete()
	
	return Response(None, status=status.HTTP_200_OK)
