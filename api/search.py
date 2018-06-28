#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.db.models import Q

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def search_missions(request):
	
	data = {

		'missions':[],
		'potential':None,
	}
	
	# Missions data
	
	results = Mission.objects.filter(mosaic__isnull=True).filter(Q(name__icontains=request.data['text']) | Q(title__icontains=request.data['text']) | Q(creator__icontains=request.data['text']))
	for mission_obj in results:
		data['missions'].append(mission_obj.getOverviewData())
	
	# Potential data
	
	results = Potential.objects.filter(title=request.data['text'])
	if results.count() > 0:
		potential_obj = results[0]
		data['potential'] = potential_obj.getOverviewData()
	
	return Response(data, status=status.HTTP_200_OK)
	
	
	
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def search_mosaics(request):
	
	data = {
		
		'mosaics':[],
		'waitings':[],
		'missions':[],
		'potentials':[],
	}
	
	# Mosaics data
	
	results = Mosaic.objects.filter(Q(creators__icontains=request.data['text']) | Q(title__icontains=request.data['text']) | Q(city__name__icontains=request.data['text']))
	for mosaic_obj in results:
		data['mosaics'].append(mosaic_obj.getOverviewData())
	
	# Waiting data
	
	results = Waiting.objects.filter(Q(title__icontains=request.data['text']) | Q(city__name__icontains=request.data['text']))
	for waiting_obj in results:
		data['waitings'].append(waiting_obj.getOverviewData())
	
	# Potentials data
	
	results = Potential.objects.filter(Q(title__icontains=request.data['text']) | Q(city__name__icontains=request.data['text']))
	for potential_obj in results:
		data['potentials'].append(potential_obj.getOverviewData())
	
	# Missions data
	
	results = Mission.objects.filter(mosaic__isnull=True).filter(Q(creator__icontains=request.data['text']) | Q(title__icontains=request.data['text']))
	for mission_obj in results:
		data['missions'].append(mission_obj.getOverviewData())

	# Empty search
	
	if not request.user.is_superuser and len(data['mosaics']) == 0 and len(data['potentials']) == 0 and len(data['missions']) == 0:
		search = Search(name=request.data['text'])
		search.save()
			
	return Response(data, status=status.HTTP_200_OK)
	
	
	
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def search_city(request):
	
	data = {
		
		'city':None,
	}
	
	results = City.objects.filter(name__iexact=request.data['name']).filter(Q(region__name__iexact=request.data['region_name']) | Q(region__locale__iexact=request.data['region_name'])).filter(Q(region__country__name__iexact=request.data['country_name']) | Q(region__country__locale__iexact=request.data['country_name']))
	if results.count() > 0:
		
		city_obj = results[0]
		
		city_data = {
			
			'name':city_obj.name,
			'region_name':city_obj.region.name,
			'country_name':city_obj.region.country.name,
		}
		
		data['city'] = city_data
		
	else:
		
		if not request.user.is_superuser:
			search_obj = Search(city=request.data['name'], region=request.data['region_name'], country=request.data['country_name'])
			search_obj.save()
	
	return Response(data, status=status.HTTP_200_OK)
