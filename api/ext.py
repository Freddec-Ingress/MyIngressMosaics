#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *



#---------------------------------------------------------------------------------------------------
@csrf_exempt
def ext_isMissionRegistered(request):
	
	data = []
	
	obj = json.loads(request.body)
	for item in obj:
	
		result = Mission.objects.filter(ref=item['mid'])
		if result.count() > 0:
			mission_obj = result[0]
			if mission_obj.mosaic:
				data.append({'mid':item['mid'], 'status':'completed', 'mosaicref':mission_obj.mosaic.ref, 'startLat':mission_obj.startLat, 'startLng':mission_obj.startLng})
			else:
				data.append({'mid':item['mid'], 'name':mission_obj.title, 'status':'registered', 'startLat':mission_obj.startLat, 'startLng':mission_obj.startLng})
				
		else:
			data.append({'mid':item['mid'], 'status':'notregistered'})
	
	return JsonResponse({'data':data})



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def ext_registerMission(request):

	obj = json.loads(request.body)
	
	results = Mission.objects.filter(ref=obj[0])
	if results.count() < 1:
		
		mission_obj = Mission(data=request.body)
		mission_obj.computeInternalData()

		return Response('Registered', status=status.HTTP_200_OK)
		
	else:
		
		mission_obj = results[0]
		
		if mission_obj.data != request.body:
			mission_obj.data = request.body
			mission_obj.admin = True
			mission_obj.computeInternalData()

		return Response('Updated', status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def ext_checkBounds(request):

	data = []
	
	results = Mission.objects.filter(startLat__gte=request.data['sLat'], startLng__gte=request.data['sLng']).filter(startLat__lte=request.data['nLat'], startLng__lte=request.data['nLng'])
	for mission_obj in results:
		
		mission_data = {
			
			'ref':mission_obj.ref,
			
			'startLat':mission_obj.startLat,
			'startLng':mission_obj.startLng,
		}
		
		data.append(mission_data)

	return Response(data, status=status.HTTP_200_OK)


