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
	
	results = IMCountry.objects.filter(name=country_name)
	if results.count() > 0:
		
		country_obj = results[0]
		country_obj.mosaic_count = mosaic_count
		country_obj.save()
		
	else:
		
		country_obj = IMCountry(name=country_name, count=mosaic_count)
		country_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_region(request):
	
	region_name = request.data['region_name']
	country_name = request.data['country_name']
	
	mosaic_count = int(request.data['mosaic_count'])
	
	results = IMCountry.objects.filter(name=country_name)
	if results.count() > 0:
		
		country_obj = results[0]
		
		results = IMRegion.objects.filter(country=country_obj, name=region_name)
		if results.count() > 0:
		
			region_obj = results[0]
			region_obj.mosaic_count = mosaic_count
			region_obj.save()
			
		else:
			
			region_obj = IMRegion(country=country_obj, name=region_name, count=mosaic_count)
			region_obj.save()
		
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_city(request):
	
	city_name = request.data['city_name']
	region_name = request.data['region_name']
	country_name = request.data['country_name']
	
	mosaic_count = int(request.data['mosaic_count'])
	
	results = IMCountry.objects.filter(name=country_name)
	if results.count() > 0:
		
		country_obj = results[0]
	
		results = IMRegion.objects.filter(country=country_obj, name=region_name)
		if results.count() > 0:
			
			region_obj = results[0]
			
			results = IMCity.objects.filter(region=region_obj, name=city_name)
			if results.count() > 0:
			
				city_obj = results[0]
				city_obj.mosaic_count = mosaic_count
				city_obj.save()
				
			else:
				
				city_obj = IMCity(region=region_data, name=city_name, count=mosaic_count)
				city_obj.save()
			
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_mosaic(request):
	
	city_name = request.data['city_name']
	region_name = request.data['region_name']
	country_name = request.data['country_name']
	
	mosaic_name = request.data['mosaic_name']
	mission_count = int(request.data['mission_count'])
	
	results = IMMosaic.objects.filter(country_name=country_name, region_name=region_name, city_name=city_name, name=mosaic_name)
	if results.count() < 1:
	
		mosaic_obj = IMMosaic(country_name=country_name, region_name=region_name, city_name=city_name, name=mosaic_name, count=mission_count)
		mosaic_obj.save()
			
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_mosaic_die(request):
	
	mosaic_obj = IMMosaic.objects.get(pk=request.data['id'])
	mosaic_obj.dead = True
	mosaic_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def im_mosaic_exclude(request):
	
	mosaic_obj = IMMosaic.objects.get(pk=request.data['id'])
	mosaic_obj.excluded = True
	mosaic_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)
