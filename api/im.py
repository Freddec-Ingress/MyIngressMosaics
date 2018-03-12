#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_country(request):
	
	country_name = request.data['country_name']
	mosaic_count = int(request.data['mosaic_count'])
	
	country_data = IMCountry.objects.filter(name=country_name)
	if country_data.count() > 0:
		
		country_data = country_data[0]
		country_data.mosaic_count = mosaic_count
		country_data.save()
		
	else:
		
		country_data = IMCountry(name=country_name, count=mosaic_count)
		country_data.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_region(request):
	
	country_name = request.data['country_name']
	region_name = request.data['region_name']
	mosaic_count = int(request.data['mosaic_count'])
	
	country_data = IMCountry.objects.filter(name=country_name)
	if country_data.count() > 0:
		
		country_data = country_data[0]
		
		region_data = IMRegion.objects.filter(country=country_data, name=region_name)
		if region_data.count() > 0:
		
			region_data = region_data[0]
			region_data.mosaic_count = mosaic_count
			region_data.save()
			
		else:
			
			region_data = IMRegion(country=country_data, name=region_name, count=mosaic_count)
			region_data.save()
		
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_city(request):
	
	country_name = request.data['country_name']
	region_name = request.data['region_name']
	city_name = request.data['city_name']
	mosaic_count = int(request.data['mosaic_count'])
	
	country_data = IMCountry.objects.filter(name=country_name)
	if country_data.count() > 0:
		
		country_data = country_data[0]
	
		region_data = IMRegion.objects.filter(country=country_data, name=region_name)
		if region_data.count() > 0:
			
			region_data = region_data[0]
			
			city_data = IMCity.objects.filter(country=country_data, region=region_data, name=city_name)
			if city_data.count() > 0:
			
				city_data = city_data[0]
				city_data.mosaic_count = mosaic_count
				city_data.save()
				
			else:
				
				city_data = IMCity(country=country_data, region=region_data, name=city_name, count=mosaic_count)
				city_data.save()
			
	return Response(None, status=status.HTTP_200_OK)
