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
			m = result[0]
			if m.mosaic:
				mdata = m.mosaic.overviewSerialize()
				if mdata['has_fake']:
					data.append({'mid':item['mid'], 'status': 'incomplete'})
				else:
					data.append({'mid':item['mid'], 'status': 'completed'})
			else:
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
		
		if m['ref'] == 'Unavailable':
			
			item = Mission(data='{}', title='Fake mission', ref='Unavailable-'+m['order']+mosaic.ref, mosaic=mosaic, order=m['order'])
			item.save()
			
		else:
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
def mission_exclude(request):
	
	results = Mission.objects.filter(ref=request.data['ref'])
	for item in results:
		
		item.admin = False
		item.save()
		
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
		
		data = {
			'count': 0,
			'countries': [],
		}
		
		for item in results:
			
			country = {
				'mosaics': Mosaic.objects.filter(country=item['country']).count(),
				'name': item['country'],
			}
			
			data['countries'].append(country)
			
		data['count'] = Mosaic.objects.all().count()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByRegion(request, name):
	
	data = None
	
	results = Mosaic.objects.filter(country=name).values('region').distinct()
	if (results.count() > 0):
		
		data = {
			'count': 0,
			'regions': [],
		}
		
		for item in results:
			
			region = {
				'mosaics': Mosaic.objects.filter(country=name, region=item['region']).count(),
				'name': item['region'],
			}
			
			data['regions'].append(region)
	
		data['count'] = Mosaic.objects.filter(country=name).count()
	
	return Response(data, status=status.HTTP_200_OK)
	


#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByCity(request, country, name):
	
	data = None
	
	results = Mosaic.objects.filter(country=country, region=name).values('city').distinct()
	if (results.count() > 0):
		
		data = {
			'count': 0,
			'cities': [],
		}
		
		for item in results:
			
			city = {
				'mosaics': Mosaic.objects.filter(country=country, region=name, city=item['city']).count(),
				'name': item['city'],
			}
			
			data['cities'].append(city)
	
		data['count'] = Mosaic.objects.filter(country=country, region=name).count()
	
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
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		
		comment = Comment(user=request.user, mosaic=mosaic, text=request.data['text'])
		comment.save()
	
		data = comment.serialize()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_update(request):
	
	data = None
	
	result = Comment.objects.filter(pk=request.data['id'])
	if result.count() > 0:
		
		comment = result[0]
		
		comment.text = request.data['text']
		comment.save()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_delete(request):
	
	data = None
	
	result = Comment.objects.filter(pk=request.data['id'])
	if result.count() > 0:
		
		comment = result[0]

		comment.delete()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def adm_renameCity(request):
	
	data = None
	
	results = Mosaic.objects.filter(country=request.data['country'], region=request.data['region'], city=request.data['city'])
	if (results.count() > 0):
		
		for item in results:
			
			item.city = request.data['new_city']
			item.save()
	
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
@permission_classes((IsAuthenticated, ))
def data_getPotentials(request):
	
	data = None
	
	from django.db.models import Count
	
	fieldname = 'name'
	results = Mission.objects.filter(mosaic__isnull=True, admin=True).values(fieldname).order_by(fieldname).annotate(count=Count(fieldname)).order_by('-count')
	if (results.count() > 0):
		
		data = []

		for item in results:
			if item['count'] >= 3:
				
				obj = {
					'name': item[fieldname],
					'count': item['count'],
				}
				
				data.append(obj)

	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def data_getOpportunities(request):
	
	data = []
	
	currentArray = []
	
	currentArray.append({'name':'Pe Ell', 'link':'/mosaic/4144', 'city':' Pe Ell'});
	currentArray.append({'name':'Pioneer Park Exploration', 'link':'/mosaic/6824', 'city':' Olympia'});
	currentArray.append({'name':'SU Pullman Campus', 'link':'/mosaic/8482', 'city':' Pullman'});
	currentArray.append({'name':'Explorer of the 253', 'link':'/mosaic/9071', 'city':' Tacoma'});
	currentArray.append({'name':'Greenwood Art Walk', 'link':'/mosaic/20217', 'city':' Seattle'});
	currentArray.append({'name':'Black Ops', 'link':'/mosaic/21173', 'city':' Kent'});
	currentArray.append({'name':'Take a Bite out of the Westside 3', 'link':'/mosaic/22632', 'city':' Olympia'});
	currentArray.append({'name':'Port of Kingston', 'link':'/mosaic/25311', 'city':' Kingston'});
	currentArray.append({'name':'Space Needle Missions', 'link':'/mosaic/4445', 'city':' Seattle'});
	currentArray.append({'name':'Aberdeen', 'link':'/mosaic/4797', 'city':' Aberdeen'});
	currentArray.append({'name':'Explore Seattle Center', 'link':'/mosaic/6348', 'city':' Seattle'});
	currentArray.append({'name':'Explore Goldendale', 'link':'/mosaic/10773', 'city':' Goldendale'});
	currentArray.append({'name':'Kent Station Art Walk', 'link':'/mosaic/16329', 'city':' Kent'});
	currentArray.append({'name':'Chambers Creek', 'link':'/mosaic/20838', 'city':' Tacoma'});
	currentArray.append({'name':'SeaTac Airport Concourses', 'link':'/mosaic/20839', 'city':' Seattle'});
	currentArray.append({'name':'Pioneer Park', 'link':'/mosaic/10361', 'city':' Puyallup'});
	currentArray.append({'name':'Heavenly Portals of the Spokane Valley', 'link':'/mosaic/18999', 'city':' Spokane'});
	currentArray.append({'name':'Get Your Bronze SpecOps Badge', 'link':'/mosaic/19513', 'city':' Bothell'});
	currentArray.append({'name':'Federal Way Tour', 'link':'/mosaic/3853', 'city':' Federal Way'});
	currentArray.append({'name':'Trash Panda', 'link':'/mosaic/5923', 'city':' Seattle'});
	currentArray.append({'name':'Ferry Day', 'link':'/mosaic/6346', 'city':' Seattle'});
	currentArray.append({'name':'Enumclaw Butter Series', 'link':'/mosaic/6502', 'city':' Enumclaw'});
	currentArray.append({'name':'Getting to Know Bellingham', 'link':'/mosaic/7052', 'city':' Bellingham'});
	currentArray.append({'name':'Black Ops Renton', 'link':'/mosaic/11600', 'city':' Renton'});
	currentArray.append({'name':'Bainbridge Island s Historic Winslow Way', 'link':'/mosaic/12416', 'city':' Bainbridge Island'});
	currentArray.append({'name':'RainBRO', 'link':'/mosaic/14040', 'city':' Seattle'});
	currentArray.append({'name':'Rainbow Ruck', 'link':'/mosaic/14671', 'city':' Snohomish'});
	currentArray.append({'name':'Viking Settler', 'link':'/mosaic/15938', 'city':' Poulsbo'});
	currentArray.append({'name':'Krazy Kelso', 'link':'/mosaic/17185', 'city':' Kelso'});
	currentArray.append({'name':'Downtown Mount Vernon', 'link':'/mosaic/18313', 'city':' Mount Vernon'});
	currentArray.append({'name':'Explore Sedro-Woolley', 'link':'/mosaic/18314', 'city':' Sedro-Woolley'});
	currentArray.append({'name':'Path of Faith Bellingham', 'link':'/mosaic/18315', 'city':' Bellingham'});
	currentArray.append({'name':'Hack Portals Across the Solar System', 'link':'/mosaic/19001', 'city':' Bothell'});
	currentArray.append({'name':'Six Kingdoms of Life', 'link':'/mosaic/19002', 'city':' Kirkland'});
	currentArray.append({'name':'La Conner Daffodil Festival', 'link':'/mosaic/19012', 'city':' La Conner'});
	currentArray.append({'name':'TGIF - Explore Friday Harbor', 'link':'/mosaic/20202', 'city':' Friday Harbor'});
	currentArray.append({'name':'What s New - Hoquiam', 'link':'/mosaic/20405', 'city':' Hoquiam'});
	currentArray.append({'name':'Cosi Crazy Cruize', 'link':'/mosaic/21819', 'city':' Aberdeen'});
	currentArray.append({'name':'King County Libraries', 'link':'/mosaic/21853', 'city':' Mercer Island'});
	currentArray.append({'name':'Tumwater Skullgress', 'link':'/mosaic/23106', 'city':' Olympia'});
	currentArray.append({'name':'Little Family Time', 'link':'/mosaic/23314', 'city':' Arlington'});
	currentArray.append({'name':'Garden d Lights', 'link':'/mosaic/25082', 'city':' Bellevue'});
	currentArray.append({'name':'Seattle Gum Wall', 'link':'/mosaic/25386', 'city':' Seattle'});
	currentArray.append({'name':'Volunteer Park Conservatory', 'link':'/mosaic/26717', 'city':' Seattle'});
	currentArray.append({'name':'Lake to Lake Trail', 'link':'/mosaic/18992', 'city':' Bellevue'});
	currentArray.append({'name':'5 Minutes Each', 'link':'/mosaic/21387', 'city':' Olympia'});
	currentArray.append({'name':'RR at Bellevue Downtown Park', 'link':'/mosaic/18918', 'city':' Bellevue'});
	currentArray.append({'name':'Longbeach Promenade', 'link':'/mosaic/4142', 'city':' Long Beach'});
	currentArray.append({'name':'Tranquility', 'link':'/mosaic/5964', 'city':' Seattle'});
	currentArray.append({'name':'Year Animals Bothell', 'link':'/mosaic/6827', 'city':' Bothell'});
	currentArray.append({'name':'Olympic College Tour', 'link':'/mosaic/7044', 'city':' Bremerton'});
	currentArray.append({'name':'Western Washington Campus', 'link':'/mosaic/8499', 'city':' Bellingham'});
	currentArray.append({'name':'Kirkland View', 'link':'/mosaic/8952', 'city':' Kirkland'});
	currentArray.append({'name':'Explore Central Washington University', 'link':'/mosaic/9801', 'city':' Ellensburg'});
	currentArray.append({'name':'Columbia Park', 'link':'/mosaic/9806', 'city':' Kennewick'});
	currentArray.append({'name':'Tour of Gig Harbor', 'link':'/mosaic/9831', 'city':' Gig Harbor'});
	currentArray.append({'name':'Take over Tenino', 'link':'/mosaic/9877', 'city':' Tenino'});
	currentArray.append({'name':'Seattle Neighborhoods - Eastlake', 'link':'/mosaic/10160', 'city':' Seattle'});
	currentArray.append({'name':'Seattle Neighborhoods - Georgetown', 'link':'/mosaic/10161', 'city':' Seattle'});
	currentArray.append({'name':'Sunset At Brightwater', 'link':'/mosaic/10437', 'city':' Woodinville'});
	currentArray.append({'name':'View Mount Baker', 'link':'/mosaic/14098', 'city':' Bellingham'});
	currentArray.append({'name':'Northwest Trek', 'link':'/mosaic/15046', 'city':' Eatonville'});
	currentArray.append({'name':'Walking Bainbridge Island', 'link':'/mosaic/19771', 'city':' Bainbridge Island'});
	currentArray.append({'name':'The Evergreen State College', 'link':'/mosaic/20583', 'city':' Olympia'});
	currentArray.append({'name':'SODO', 'link':'/mosaic/21468', 'city':' Seattle'});
	currentArray.append({'name':'Play at the Parks', 'link':'/mosaic/22538', 'city':' Everett'});
	currentArray.append({'name':'Monorail', 'link':'/mosaic/23398', 'city':' Seattle'});
	currentArray.append({'name':'Spirit of Renton', 'link':'/mosaic/25389', 'city':' Renton'});
	currentArray.append({'name':'Ladies Get Away Cashmere Washington', 'link':'/mosaic/25757', 'city':' Cashmere'});
	currentArray.append({'name':'Tour Fort Lewis', 'link':'/mosaic/283', 'city':' Tacoma'});
	currentArray.append({'name':'Tacoma Travels', 'link':'/mosaic/288', 'city':' Tacoma'});
	currentArray.append({'name':'Spokane Tour', 'link':'/mosaic/3766', 'city':' Spokane'});
	currentArray.append({'name':'Grays Harbor Tour', 'link':'/mosaic/4141', 'city':' Amanda Park'});
	currentArray.append({'name':'Port Townsend Mission Series', 'link':'/mosaic/4222', 'city':' Port Townsend'});
	currentArray.append({'name':'Ingress Anomaly Winners', 'link':'/mosaic/4231', 'city':' Spokane'});
	currentArray.append({'name':'Explore Mason County', 'link':'/mosaic/5931', 'city':' Shelton'});
	currentArray.append({'name':'Ocean Shores Mission Series', 'link':'/mosaic/5932', 'city':' Hoquiam'});
	currentArray.append({'name':'Sunset', 'link':'/mosaic/5938', 'city':' Aberdeen'});
	currentArray.append({'name':'Century 21 Exposition', 'link':'/mosaic/6344', 'city':' Seattle'});
	currentArray.append({'name':'Seattle Obsidian Resistance', 'link':'/mosaic/6503', 'city':' Seattle'});
	currentArray.append({'name':'Welcome to Longview', 'link':'/mosaic/6905', 'city':' Longview'});
	currentArray.append({'name':'Columbia River Mission', 'link':'/mosaic/7936', 'city':' Richland'});
	currentArray.append({'name':'Bridges be Bridging', 'link':'/mosaic/8841', 'city':' La Conner'});
	currentArray.append({'name':'Downtown Richland', 'link':'/mosaic/9041', 'city':' Richland'});
	currentArray.append({'name':'A Visit to Long Beach', 'link':'/mosaic/9289', 'city':' Long Beach'});
	currentArray.append({'name':'Rainier', 'link':'/mosaic/9315', 'city':' Seattle'});
	currentArray.append({'name':'THELER', 'link':'/mosaic/9769', 'city':' Belfair'});
	currentArray.append({'name':'TC Tour', 'link':'/mosaic/9794', 'city':' Richland'});
	currentArray.append({'name':'North Washington Coast', 'link':'/mosaic/9869', 'city':' Blaine'});
	currentArray.append({'name':'International District', 'link':'/mosaic/9923', 'city':' Seattle'});
	currentArray.append({'name':'Centerville', 'link':'/mosaic/10007', 'city':' Centralia'});
	currentArray.append({'name':'Downtown Kennewick', 'link':'/mosaic/10016', 'city':' Kennewick'});
	currentArray.append({'name':'Seattle Grunge Scene', 'link':'/mosaic/10075', 'city':' Seattle'});
	currentArray.append({'name':'Seattle Neighborhoods - Central District', 'link':'/mosaic/10076', 'city':' Seattle'});
	currentArray.append({'name':'Seattle Neighborhoods - Rainier Valley', 'link':'/mosaic/10077', 'city':' Seattle'});
	currentArray.append({'name':'Seattle Neighbourhoods - Ballard', 'link':'/mosaic/10078', 'city':' Seattle'});
	currentArray.append({'name':'Tour of Anacortes', 'link':'/mosaic/10102', 'city':' Anacortes'});
	currentArray.append({'name':'Westport', 'link':'/mosaic/10114', 'city':' Westport'});
	currentArray.append({'name':'Tour of Yakima', 'link':'/mosaic/11037', 'city':' Yakima'});
	currentArray.append({'name':'Capital Stroll', 'link':'/mosaic/11308', 'city':' Olympia'});
	currentArray.append({'name':'Fort Worden', 'link':'/mosaic/11331', 'city':' Port Townsend'});
	currentArray.append({'name':'Mosaic March', 'link':'/mosaic/11642', 'city':' Longview'});
	currentArray.append({'name':'Ft Vancouver Barracks', 'link':'/mosaic/12207', 'city':' Vancouver'});
	currentArray.append({'name':'Island of the mice', 'link':'/mosaic/12680', 'city':' Oak Harbor'});
	currentArray.append({'name':'Explore Issaquah', 'link':'/mosaic/12841', 'city':' Issaquah'});
	currentArray.append({'name':'Grimm Fairy Tales', 'link':'/mosaic/13842', 'city':' Bothell'});
	currentArray.append({'name':'KRAKEN Series', 'link':'/mosaic/14087', 'city':' Bremerton'});
	currentArray.append({'name':'Tacoma Star -  Banner Mission', 'link':'/mosaic/14423', 'city':' Tacoma'});
	currentArray.append({'name':'Perusing Port Orchard', 'link':'/mosaic/14864', 'city':' Port Orchard'});
	currentArray.append({'name':'Central District Candy Land', 'link':'/mosaic/15799', 'city':' Seattle'});
	currentArray.append({'name':'Birds nest', 'link':'/mosaic/16037', 'city':' Seattle'});
	currentArray.append({'name':'Bellevue City', 'link':'/mosaic/16038', 'city':' Bellevue'});
	currentArray.append({'name':'Ruck the Parks', 'link':'/mosaic/16674', 'city':' Bothell'});
	currentArray.append({'name':'Moses Lake Sunset', 'link':'/mosaic/16865', 'city':' Moses Lake'});
	currentArray.append({'name':'Cap Hill Ingress Pride 2017', 'link':'/mosaic/17534', 'city':' Seattle'});
	currentArray.append({'name':'Downtown Everett Walking Tour', 'link':'/mosaic/18458', 'city':' Everett'});
	currentArray.append({'name':'Explore downtown Edmonds', 'link':'/mosaic/18459', 'city':' Edmonds'});
	currentArray.append({'name':'Melting of Olympia', 'link':'/mosaic/18597', 'city':' Olympia'});
	currentArray.append({'name':'Wolf Territory Original', 'link':'/mosaic/18598', 'city':' Tacoma'});
	currentArray.append({'name':'Leavenworth', 'link':'/mosaic/18678', 'city':' Leavenworth'});
	currentArray.append({'name':'Everett Blackbird', 'link':'/mosaic/18993', 'city':' Everett'});
	currentArray.append({'name':'Doing the Puyallup', 'link':'/mosaic/18998', 'city':' Puyallup'});
	currentArray.append({'name':'Points of Polygonz', 'link':'/mosaic/19265', 'city':' Bellingham'});
	currentArray.append({'name':'Let s KENT', 'link':'/mosaic/21104', 'city':' Kent'});
	currentArray.append({'name':'Namaste Supreme  Trash Panda', 'link':'/mosaic/21337', 'city':' Puyallup'});
	currentArray.append({'name':'Nerds', 'link':'/mosaic/21469', 'city':' Seattle'});
	currentArray.append({'name':'Yelm Banner', 'link':'/mosaic/23105', 'city':' Olympia'});
	currentArray.append({'name':'Seattle  Green Lake', 'link':'/mosaic/23476', 'city':' Seattle'});
	currentArray.append({'name':'Lake Union', 'link':'/mosaic/23670', 'city':' Seattle'});
	currentArray.append({'name':'Fireworks over Lake Union', 'link':'/mosaic/23673', 'city':' Seattle'});
	currentArray.append({'name':'Historic Silverdale', 'link':'/mosaic/23775', 'city':' Silverdale'});
	currentArray.append({'name':'The Duck Stops Here', 'link':'/mosaic/24370', 'city':' Tacoma'});
	currentArray.append({'name':'Wolf Territory', 'link':'/mosaic/24371', 'city':' Tacoma'});
	currentArray.append({'name':'Chambers Bay', 'link':'/mosaic/24378', 'city':' Tacoma'});
	currentArray.append({'name':'The Kinship of the Link Cat', 'link':'/mosaic/24528', 'city':' Olympia'});
	currentArray.append({'name':'Auburn Exploration', 'link':'/mosaic/24720', 'city':' Auburn'});
	currentArray.append({'name':'North Rainier-Enumclaw Elk Herd', 'link':'/mosaic/24843', 'city':' Enumclaw'});
	currentArray.append({'name':'Buckley Steam Donkey', 'link':'/mosaic/24844', 'city':' Buckley'});
	currentArray.append({'name':'Let s Stroll the Ave', 'link':'/mosaic/25113', 'city':' Wenatchee'});
	currentArray.append({'name':'No One Sings Like You Anymore', 'link':'/mosaic/25857', 'city':' Quincy'});
	currentArray.append({'name':'Juanita Bay Sunset', 'link':'/mosaic/26718', 'city':' Kirkland'});
	currentArray.append({'name':'MissionDay  Seattle', 'link':'/mosaic/6549', 'city':' Seattle'});
	currentArray.append({'name':'Lake to Lake', 'link':'/mosaic/18991', 'city':' Bellevue'});
	currentArray.append({'name':'Raymond Theatre', 'link':'/mosaic/4143', 'city':' Raymond'});
	currentArray.append({'name':'Grant County WA', 'link':'/mosaic/5900', 'city':' Moses Lake'});
	currentArray.append({'name':'Obsidian Seattle', 'link':'/mosaic/6504', 'city':' Seattle'});
	currentArray.append({'name':'Tour of Tacoma', 'link':'/mosaic/6826', 'city':' Tacoma'});
	currentArray.append({'name':'Ellensburg Mission Series', 'link':'/mosaic/7736', 'city':' Ellensburg'});
	currentArray.append({'name':'UW Cherry Blossoms', 'link':'/mosaic/7895', 'city':' Seattle'});
	currentArray.append({'name':'Connecting Whidbey Island', 'link':'/mosaic/7941', 'city':' Anacortes'});
	currentArray.append({'name':'North Kitsap Mission Series', 'link':'/mosaic/9879', 'city':' Poulsbo'});
	currentArray.append({'name':'Admiralty Inlet Sunset', 'link':'/mosaic/15867', 'city':' Oak Harbor'});
	currentArray.append({'name':'Tour Silver Lake', 'link':'/mosaic/17072', 'city':' Everett'});
	currentArray.append({'name':'Snohomish to Bryant', 'link':'/mosaic/17860', 'city':' Snohomish'});
	currentArray.append({'name':'ENL Ladies Fall Getaway', 'link':'/mosaic/27943', 'city':' Longview'});
	currentArray.append({'name':'Does what s beneath the Sound eternal lie', 'link':'/mosaic/287', 'city':' Allyn-Grapeview'});
	currentArray.append({'name':'Tour of PLU', 'link':'/mosaic/6825', 'city':' Tacoma'});
	currentArray.append({'name':'Blaine  WA', 'link':'/mosaic/13718', 'city':' Blaine'});
	currentArray.append({'name':'Cowboy Viking Crossover', 'link':'/mosaic/25851', 'city':' Raymond'});
	currentArray.append({'name':'NYC in Seattle', 'link':'/mosaic/27338', 'city':' Seattle'});
	currentArray.append({'name':'Alphabet Missions', 'link':'/mosaic/4376', 'city':' Seattle'});
	currentArray.append({'name':'Capitol Bread Crumbs', 'link':'/mosaic/7866', 'city':' Olympia'});
	currentArray.append({'name':'Reswue is for Dating Mosaic', 'link':'/mosaic/12608', 'city':' Spokane'});
	currentArray.append({'name':'Chief Sealth', 'link':'/mosaic/4155', 'city':' Seattle'});
	currentArray.append({'name':'Heart Box Baby Mosaic', 'link':'/mosaic/3586', 'city':' Seattle'});
	currentArray.append({'name':'Cascadia Flag', 'link':'/mosaic/4157', 'city':' Seattle'});

	for item in currentArray:
		
		results = Mosaic.objects.filter(title__icontains=item['name'])
		if results.count() < 1:
			data.append(item)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def adm_excludePotential(request):
	
	results = Mission.objects.filter(mosaic__isnull=True, name=request.data['name'])
	for item in results:
		
		item.admin = False
		item.save()
	
	return Response(None, status=status.HTTP_200_OK)
