#!/usr/bin/env python
# coding: utf-8

import json

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token

from rest_social_auth.serializers import UserTokenSerializer

from .models import *

from django.http import HttpResponse

from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model, authenticate, logout

from operator import itemgetter, attrgetter, methodcaller



#---------------------------------------------------------------------------------------------------
@csrf_exempt
def ext_isMissionRegistered(request):
	
	data = []
	
	obj = json.loads(request.body)
	for item in obj:
	
		result = Mission.objects.filter(ref = item['mid'])
		if result.count() > 0:
			data.append({'mid':item['mid'], 'status': 'registered'})
		else:
			data.append({'mid':item['mid'], 'status': 'notregistered'})
	
	from django.http import JsonResponse
	return JsonResponse({'data': data})



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def ext_registerMission(request):

	obj = json.loads(request.body)
	
	results = Mission.objects.filter(ref=obj[0])
	if (results.count() < 1):
		
		mission = Mission(data=request.body)
		mission.save()
		
		mission.computeInternalData()
		
		return Response('Registered', status=status.HTTP_200_OK)
		
	else:
		
		mission = results[0]
		
		if mission.data != request.body:
		
			mission.data = request.body
			mission.save()
			
			mission.computeInternalData()

	return Response('Updated', status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def ext_checkBounds(request):

	data = None
	
	results = Mission.objects.filter(startLat__gte=request.data['sLat'], startLng__gte=request.data['sLng']).filter(startLat__lte=request.data['nLat'], startLng__lte=request.data['nLng'])
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			
			mission = item.mapSerialize()
			data.append(mission)

	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_login(request):
	
	user = authenticate(username=request.data['username'], password=request.data['password'])
	if user is None:
		return Response('error_USER_UNKNOWN', status=status.HTTP_400_BAD_REQUEST)
	
	return Response(UserTokenSerializer(user).data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_register(request):
	
	if request.data['password1'] != request.data['password2']:
		return Response('error_PASSWORDS_NOT_EQUAL', status=status.HTTP_400_BAD_REQUEST)

	try:
	
		user = get_user_model().objects.create_user(request.data['username'], request.data['email'], request.data['password1'])
		
	except IntegrityError:
		
		results = get_user_model().objects.filter(username=request.data['username'])
		if results.count() > 0:
			return Response('error_USERNAME_ALREADY_EXISTS', status=status.HTTP_400_BAD_REQUEST)
		
		return Response('error_INTEGRITY_ERROR', status=status.HTTP_400_BAD_REQUEST)
	
	token = Token.objects.create(user=user)
	
	authenticate(username=request.data['username'], password=request.data['password1'])
	
	return Response(UserTokenSerializer(user).data, status=status.HTTP_201_CREATED)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_logout(request):
	
	logout(request)
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def user_getDetails(request):
	
	data = {
		'loved': [],
		'completed': [],
	}
	
	results = request.user.mosaics_loved.all()
	if results.count() > 0:
		for item in results:
			
			mosaic = item.overviewSerialize()
			data['loved'].append(mosaic)
	
	results = request.user.mosaics_completed.all()
	if results.count() > 0:
		for item in results:
			
			mosaic = item.overviewSerialize()
			data['completed'].append(mosaic)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def user_getProfile(request):
	
	data = {
		'name': request.user.username,
		'faction': None,
		'superuser': request.user.is_superuser,
	}
	
	if request.user.profile:
		data['faction'] = request.user.profile.faction
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def user_edit(request):
	
	request.user.username = request.data['name']
	request.user.save()
	
	request.user.profile.faction = request.data['faction']
	request.user.profile.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def user_getRegisteredMissions(request):
	
	missions = None
	
	results = Mission.objects.filter(mosaic__isnull = True).order_by('title')
	if results.count() > 0:
		
		missions = []
		for item in results:
			
			temp = item.overviewSerialize()
			missions.append(temp)
	
	return Response(missions, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_create(request):
	
	mosaic = Mosaic(	registerer = request.user,
						cols = int(request.data['columns']),
						type = request.data['type'],
						city = request.data['city'],
						title = request.data['title'],
						region = request.data['region'],
						country = request.data['country']
					)
	mosaic.save()
	
	for m in request.data['missions']:
		
		result = Mission.objects.filter(ref=m['ref'])
		if result.count() > 0:
			
			item = result[0]
			item.mosaic = mosaic
			item.order = m['order']
			item.save()
	
	mosaic.computeInternalData()
	
	return Response(mosaic.ref, status=status.HTTP_200_OK)

	
	
#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def mosaic_view(request, ref):
	
	data = None
	
	result = Mosaic.objects.filter(ref=ref)
	if result.count() > 0:
		
		mosaic = result[0]
		data = mosaic.detailsSerialize()
		
		if mosaic.lovers.filter(username=request.user.username).count() > 0:
			data['is_loved'] = True
		
		if mosaic.completers.filter(username=request.user.username).count() > 0:
			data['is_completed'] = True
			
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_edit(request):
	
	if request.user.is_superuser:
		result = Mosaic.objects.filter(ref=request.data['ref'])
	else:
		result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
	
	if result.count() > 0:
		mosaic = result[0]
		
		mosaic.city = request.data['city']
		mosaic.type = request.data['type']
		mosaic.cols = request.data['cols']
		mosaic.title = request.data['title']
		mosaic.region = request.data['region']
		mosaic.country = request.data['country']
		
		mosaic.save()
	
		data = mosaic.detailsSerialize()
		return Response(data, status=status.HTTP_200_OK)
		
	return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_reorder(request):

	if request.user.is_superuser:
		result = Mosaic.objects.filter(ref=request.data['ref'])
	else:
		result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
	
	if result.count() > 0:
		mosaic = result[0]
		
		for item in request.data['missions']:
			
			result = Mission.objects.filter(ref=item['ref'])
			if result.count() > 0:
				mission = result[0]
				
				mission.order = item['order']
				mission.save()
	
		mosaic.save()
		
		data = mosaic.detailsSerialize()
		return Response(data, status=status.HTTP_200_OK)

	return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_delete(request):
	
	if request.user.is_superuser:
		result = Mosaic.objects.filter(ref=request.data['ref'])
	else:
		result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
	
	if result.count() > 0:
		
		mosaic = result[0]
		mosaic.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_removeMission(request):
	
	if request.user.is_superuser:
		result = Mosaic.objects.filter(ref=request.data['ref'])
	else:
		result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
	
	if result.count() > 0:
		
		mosaic = result[0]
		
		result = Mission.objects.filter(ref=request.data['mission'], mosaic=mosaic)
		if result.count() > 0:
			
			mission = result[0]
			
			mission.mosaic = None
			mission.save()
			
			mosaic.save()
			
			data = mosaic.serialize()
			return Response(data, status=status.HTTP_200_OK)
	
	return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_addMission(request):
	
	if request.user.is_superuser:
		result = Mosaic.objects.filter(ref=request.data['ref'])
	else:
		result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
	
	if result.count() > 0:
		
		mosaic = result[0]
		
		result = Mission.objects.filter(ref=request.data['mission'], mosaic__isnull=True)
		if result.count() > 0:
			
			mission = result[0]
			
			mission.mosaic = mosaic
			mission.order = request.data['order']
			mission.save()
			
			mosaic.save()
			
			data = mosaic.serialize()
			return Response(data, status=status.HTTP_200_OK)
	
	return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_love(request):
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		result = mosaic.lovers.filter(username=request.user.username)
		if result.count() < 1:
			
			mosaic.lovers.add(request.user)
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_unlove(request):
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		result = mosaic.lovers.filter(username=request.user.username)
		if result.count() > 0:
			
			mosaic.lovers.remove(request.user)
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_complete(request):
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		result = mosaic.completers.filter(username=request.user.username)
		if result.count() < 1:
			
			mosaic.completers.add(request.user)
			
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_uncomplete(request):
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		result = mosaic.completers.filter(username=request.user.username)
		if result.count() > 0:
			
			mosaic.completers.remove(request.user)
			
	return Response(None, status=status.HTTP_200_OK)
	
	
	
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mission_delete(request):
	
	result = Mission.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		result[0].delete();
		
	return Response(None, status=status.HTTP_200_OK)
	
	
	
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mission_order(request):
	
	result = Mission.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mission = result[0]
		
		mission.order = request.data['order']
		mission.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByCountry(request):
	
	data = None
	
	results = Mosaic.objects.values('country').distinct()
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			
			country = {
				'mosaics': Mosaic.objects.filter(country=item['country']).count(),
				'name': item['country'],
			}
			
			data.append(country)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByRegion(request, name):
	
	data = None
	
	results = Mosaic.objects.filter(country=name).values('region').distinct()
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			
			region = {
				'mosaics': Mosaic.objects.filter(country=name, region=item['region']).count(),
				'name': item['region'],
			}
			
			data.append(region)
	
	return Response(data, status=status.HTTP_200_OK)
	


#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByCity(request, country, name):
	
	data = None
	
	results = Mosaic.objects.filter(country=country, region=name).values('city').distinct()
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			
			city = {
				'mosaics': Mosaic.objects.filter(country=country, region=name, city=item['city']).count(),
				'name': item['city'],
			}
			
			data.append(city)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsOfCity(request, country, region, name):
	
	results = Mosaic.objects.filter(country=country, region=region, city=name).order_by('-pk')
	if results.count() > 0:
		
		data = []
		
		for item in results:
			
			mosaic = item.overviewSerialize()
			data.append(mosaic)
		
		return Response(data, status=status.HTTP_200_OK)
		
	return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def data_searchForMissions(request):
	
	results = Mission.objects.filter(mosaic__isnull=True).filter(Q(title__icontains=request.data['text']) | Q(creator__icontains=request.data['text'])).order_by('creator', 'title')
	if (results.count() > 0):

		data = { 'missions': [], }
		for item in results:
			data['missions'].append(item.overviewSerialize())
	
	else:
		data = { 'missions': None, }
	
	return Response(data, status=status.HTTP_200_OK)
    
    
    
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def data_searchForMosaics(request):
	
	array = []
	
	# Creator search
	
	results = Mosaic.objects.filter(creators__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
		
	# Title search
	
	results = Mosaic.objects.filter(title__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
		
	# Country search
	
	results = Mosaic.objects.filter(country__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
		
	# Region search
	
	results = Mosaic.objects.filter(region__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
		
	# City search
	
	results = Mosaic.objects.filter(city__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
				
	if (len(array) > 0):
		
		temp = list(set(array))
		
		data = { 'mosaics': [], }
		for item in temp:
			data['mosaics'].append(item.overviewSerialize())
	
	else:
		data = { 'mosaics': [], }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def map_getMosaics(request):
	
	data = None
	
	results = Mosaic.objects.filter(startLat__gte=request.data['sLat'], startLng__gte=request.data['sLng']).filter(startLat__lte=request.data['nLat'], startLng__lte=request.data['nLng'])
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			
			mosaic = item.mapSerialize()
			data.append(mosaic)

	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def map_getMosaicOverview(request):
	
	data = None
	
	results = Mosaic.objects.filter(ref=request.data['ref'])
	if (results.count() > 0):
		
		data = []
		
		item = results[0]
		
		mosaic = item.overviewSerialize()
		data.append(mosaic)

	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_add(request):
	
	data = None
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_update(request):
	
	data = None
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_delete(request):
	
	data = None
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def adm_getCountries(request):
	
	data = None
	
	results = Mosaic.objects.values('country').order_by('country').distinct()
	if (results.count() > 0):
		
		data = { 'countries': [], }
		
		for item in results:
			
			country = {
				'name': item['country'],
			}
			
			data['countries'].append(country)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def adm_getRegions(request):
	
	data = None
	
	results = Mosaic.objects.filter(country=request.data['country']).values('region').order_by('region').distinct()
	if (results.count() > 0):
		
		data = { 'regions': [], }
		
		for item in results:
			
			region = {
				'name': item['region'],
			}
			
			data['regions'].append(region)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def adm_renameRegion(request):
	
	data = None
	
	results = Mosaic.objects.filter(country=request.data['country'], region=request.data['region'])
	if (results.count() > 0):
		
		for item in results:
			
			item.region = request.data['new_region']
			item.save()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def adm_getMosaics(request):
	
	data = None
	
	from django.db.models import Count
	
	fieldname = 'name'
	results = Mission.objects.filter(mosaic__isnull=True).values(fieldname).order_by(fieldname).annotate(count=Count(fieldname)).order_by('-count')
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			if item['count'] >= 6:
				
				obj = {
					'name': item[fieldname],
					'count': item['count'],
				}
				
				data.append(obj)
	
	return Response(data, status=status.HTTP_200_OK)
