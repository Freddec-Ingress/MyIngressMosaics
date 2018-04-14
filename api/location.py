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
def city_list(request):
	
	data = {
		
		'cities':[],
	}
	
	# Cities data
	
	city_results = City.objects.filter(region__id=request.data['region_id']).order_by('name')
	for city_obj in city_results:
		
		city_data = {
			
			'id':city_obj.pk,
			'name':city_obj.name,
		}
		
		data['cities'].append(city_data)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_merge(request):
	
	src_city_obj = City.objects.get(id=request.data['src_city_id'])
	dst_city_obj = City.objects.get(id=request.data['dst_city_id'])
	
	for mosaic_obj in src_city_obj.mosaics.all():
		mosaic_obj.city = dst_city_obj
		mosaic_obj.save()

	if src_city_obj.mosaics.all().count() < 1:
		src_city_obj.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_list(request):
	
	data = {
		
		'regions':[],
	}
	
	# Regions data
	
	region_results = Region.objects.filter(country__id=request.data['country_id']).order_by('name')
	for region_obj in region_results:
		
		region_data = {
			
			'id':region_obj.pk,
			'name':region_obj.name,
		}
		
		data['regions'].append(region_data)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def country_list(request):
	
	data = {
		
		'countries':[],
	}
	
	# Countries data
	
	country_results = Country.objects.all().order_by('name')
	for country_obj in country_results:
		
		country_data = {
			
			'id':country_obj.pk,
			'name':country_obj.name,
		}
		
		data['countries'].append(country_data)
	
	return Response(data, status=status.HTTP_200_OK)
