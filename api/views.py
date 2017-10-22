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
	
	currentArray.append({'name':'OceanGate', 'link':'/mosaic/550', 'city':' Tuckerton'});
	currentArray.append({'name':'NYC Skyline NJ', 'link':'/mosaic/3693', 'city':' Weehawken'});
	currentArray.append({'name':'Serene Colts Neck', 'link':'/mosaic/7187', 'city':' Scobeyville'});
	currentArray.append({'name':'I own Kearny', 'link':'/mosaic/559', 'city':' Kearny'});
	currentArray.append({'name':'Burnout', 'link':'/mosaic/3609', 'city':' Saddle Brook'});
	currentArray.append({'name':'Jonas Cattell', 'link':'/mosaic/5820', 'city':' Haddonfield'});
	currentArray.append({'name':'Visiting Watchung Reservation', 'link':'/mosaic/5953', 'city':' Berkeley Heights'});
	currentArray.append({'name':'Tuckerton Mosaic', 'link':'/mosaic/7045', 'city':' Tuckerton'});
	currentArray.append({'name':'Sugar Skulls', 'link':'/mosaic/7049', 'city':' Berkeley Township'});
	currentArray.append({'name':'Pitman', 'link':'/mosaic/9252', 'city':' Pitman'});
	currentArray.append({'name':'St  Mary Cemetery', 'link':'/mosaic/9370', 'city':' Bellmawr'});
	currentArray.append({'name':'Visit Lincoln Park', 'link':'/mosaic/9903', 'city':' Lincoln Park'});
	currentArray.append({'name':'Wildlife', 'link':'/mosaic/10581', 'city':' Wyckoff'});
	currentArray.append({'name':'Brandon Farms', 'link':'/mosaic/11204', 'city':' Pennington'});
	currentArray.append({'name':'First Ocean County 9 on Nine', 'link':'/mosaic/12106', 'city':' Tuckerton'});
	currentArray.append({'name':'Wenonah', 'link':'/mosaic/13470', 'city':' 0'});
	currentArray.append({'name':'Hack the elements and save the world', 'link':'/mosaic/14230', 'city':' New Brunswick'});
	currentArray.append({'name':'Justice Cats Of Ameowrica', 'link':'/mosaic/17741', 'city':' Lodi'});
	currentArray.append({'name':'CatVengers', 'link':'/mosaic/17787', 'city':' Saddle Brook'});
	currentArray.append({'name':'The Barnegat Venture', 'link':'/mosaic/18132', 'city':' Barnegat'});
	currentArray.append({'name':'Trenton South Riverwalk Park', 'link':'/mosaic/18250', 'city':' Trenton'});
	currentArray.append({'name':'Visiting Bound Brook  NJ', 'link':'/mosaic/19423', 'city':' Bound Brook'});
	currentArray.append({'name':'C A T S', 'link':'/mosaic/19826', 'city':' Ridgewood'});
	currentArray.append({'name':'Turtle Back Zoo', 'link':'/mosaic/20490', 'city':' West Orange'});
	currentArray.append({'name':'Get Off the Boardwalk', 'link':'/mosaic/21558', 'city':' Seaside Heights'});
	currentArray.append({'name':'Explore the Columbia Trail', 'link':'/mosaic/23079', 'city':' High Bridge'});
	currentArray.append({'name':'Historic Matawan Medals', 'link':'/mosaic/24821', 'city':' Matawan'});
	currentArray.append({'name':'Old Bridge Tour', 'link':'/mosaic/6358', 'city':' Old Bridge Township'});
	currentArray.append({'name':'EVOLUTION REVOLUTION', 'link':'/mosaic/1968', 'city':' Fort Lee'});
	currentArray.append({'name':'Jersey City Waterfront', 'link':'/mosaic/3694', 'city':' Jersey City'});
	currentArray.append({'name':'Tour of Bergen County', 'link':'/mosaic/3722', 'city':' Saddle Brook'});
	currentArray.append({'name':'Mysterious Cats', 'link':'/mosaic/4260', 'city':' Glen Rock'});
	currentArray.append({'name':'Historic Haddonfield Mosaic', 'link':'/mosaic/5475', 'city':' Haddonfield'});
	currentArray.append({'name':'Davies Sports Complex', 'link':'/mosaic/5641', 'city':' 0'});
	currentArray.append({'name':'Town of Boonton', 'link':'/mosaic/5950', 'city':' Boonton'});
	currentArray.append({'name':'Visiting Denville', 'link':'/mosaic/5951', 'city':' Denville'});
	currentArray.append({'name':'Little Egg Harbor', 'link':'/mosaic/7438', 'city':' Tuckerton'});
	currentArray.append({'name':'Visiting Somerville', 'link':'/mosaic/8546', 'city':' Somerville'});
	currentArray.append({'name':'Alcyon Park', 'link':'/mosaic/8734', 'city':' Pitman'});
	currentArray.append({'name':'Barnegat Light Explored', 'link':'/mosaic/8788', 'city':' Barnegat Light'});
	currentArray.append({'name':'Bayonne Bridge', 'link':'/mosaic/8797', 'city':' Jersey City'});
	currentArray.append({'name':'Calico', 'link':'/mosaic/11080', 'city':' Middletown'});
	currentArray.append({'name':'Visiting Westfield', 'link':'/mosaic/11295', 'city':' Westfield'});
	currentArray.append({'name':'Phillipsburg', 'link':'/mosaic/11639', 'city':' Phillipsburg'});
	currentArray.append({'name':'Stafford Mission', 'link':'/mosaic/12107', 'city':' Stafford Township'});
	currentArray.append({'name':'Central Jersey Jew', 'link':'/mosaic/13793', 'city':' Keyport'});
	currentArray.append({'name':'Visiting Peapack Glastone  NJ', 'link':'/mosaic/14000', 'city':' Peapack'});
	currentArray.append({'name':'Cheesequake Farm', 'link':'/mosaic/19779', 'city':' Old Bridge Township'});
	currentArray.append({'name':'Zombiegress', 'link':'/mosaic/19824', 'city':' paramus'});
	currentArray.append({'name':'Moomins of Saddle Brook', 'link':'/mosaic/23555', 'city':' Saddle Brook'});
	currentArray.append({'name':'Clifton NA Heads', 'link':'/mosaic/22310', 'city':' Clifton'});
	currentArray.append({'name':'Pamachapura', 'link':'/mosaic/5146', 'city':' Glen Rock'});
	currentArray.append({'name':'Visiting Summit NJ', 'link':'/mosaic/5952', 'city':' Summit'});
	currentArray.append({'name':'Remembering Sandy', 'link':'/mosaic/10071', 'city':' Belmar'});
	currentArray.append({'name':'Tour of Fair Lawn', 'link':'/mosaic/10103', 'city':' Fair Lawn'});
	currentArray.append({'name':'Palisades Conquest', 'link':'/mosaic/10582', 'city':' Edgewater'});
	currentArray.append({'name':'Downtown Metuchen', 'link':'/mosaic/10734', 'city':' Metuchen'});
	currentArray.append({'name':'Seek Enlightenment in CNJ', 'link':'/mosaic/10735', 'city':' Sayreville'});
	currentArray.append({'name':'Red Bank Battlefield Tour', 'link':'/mosaic/11092', 'city':' National Park'});
	currentArray.append({'name':'Visit Perth Amboy', 'link':'/mosaic/12547', 'city':' Perth Amboy'});
	currentArray.append({'name':'Woodbridge Knights of Ren', 'link':'/mosaic/13446', 'city':' Woodbridge Township'});
	currentArray.append({'name':'OCNJ 14th Street Pier', 'link':'/mosaic/13594', 'city':' Ocean City'});
	currentArray.append({'name':'Cool Cat', 'link':'/mosaic/14051', 'city':' Point Pleasant Beach'});
	currentArray.append({'name':'Victory', 'link':'/mosaic/15810', 'city':' Perth Amboy'});
	currentArray.append({'name':'John Bull', 'link':'/mosaic/15811', 'city':' South Amboy'});
	currentArray.append({'name':'Exploring Cook-Douglass', 'link':'/mosaic/15831', 'city':' New Brunswick'});
	currentArray.append({'name':'Woodbury NJ', 'link':'/mosaic/16000', 'city':' Woodbury'});
	currentArray.append({'name':'Newark s Broad Street Station', 'link':'/mosaic/16106', 'city':' Newark'});
	currentArray.append({'name':'Newark Airport', 'link':'/mosaic/16261', 'city':' Newark'});
	currentArray.append({'name':'City Of Orange', 'link':'/mosaic/16362', 'city':' East Orange'});
	currentArray.append({'name':'Essex County Parks   Recreation', 'link':'/mosaic/16680', 'city':' Montclair'});
	currentArray.append({'name':'Keansburg  NJ Amusement Park', 'link':'/mosaic/17094', 'city':' Keansburg'});
	currentArray.append({'name':'Higher than the Trees', 'link':'/mosaic/20357', 'city':' Manchester Township'});
	currentArray.append({'name':'The Thin Blue Line', 'link':'/mosaic/20624', 'city':' Hawthorne'});
	currentArray.append({'name':'Welcome To The Meadowlands', 'link':'/mosaic/24473', 'city':' Lyndhurst'});
	currentArray.append({'name':'SS Atlantus Banner', 'link':'/mosaic/25843', 'city':' Cape May'});
	currentArray.append({'name':'Why So Serious', 'link':'/mosaic/25858', 'city':' Bloomfield'});
	currentArray.append({'name':'OCNJ Lifeboat', 'link':'/mosaic/27791', 'city':' Ocean City'});
	currentArray.append({'name':'MD  Hoboken  Columbus Park', 'link':'/mosaic/27808', 'city':' Hoboken'});
	currentArray.append({'name':'Walking Historical Morristown', 'link':'/mosaic/2708', 'city':' Morristown'});
	currentArray.append({'name':'Bergen County', 'link':'/mosaic/3721', 'city':' Rutherford'});
	currentArray.append({'name':'Somerset County', 'link':'/mosaic/4253', 'city':' Somerville'});
	currentArray.append({'name':'Ocean City Boardwalk', 'link':'/mosaic/5610', 'city':' Ocean City'});
	currentArray.append({'name':'Barnegat Branch Trail', 'link':'/mosaic/7487', 'city':' Toms River'});
	currentArray.append({'name':'Central Jersey old bridge Hunter', 'link':'/mosaic/13444', 'city':' Keyport'});
	currentArray.append({'name':'Central Jersey Sith', 'link':'/mosaic/13445', 'city':' South Amboy'});
	currentArray.append({'name':'Paying Respects', 'link':'/mosaic/14454', 'city':' Closter'});
	currentArray.append({'name':'Historic Somerville  NJ', 'link':'/mosaic/15942', 'city':' Somerville'});
	currentArray.append({'name':'Rahway Prison', 'link':'/mosaic/16985', 'city':' Rahway'});
	currentArray.append({'name':'The Thin Red Line of Courage', 'link':'/mosaic/21242', 'city':' Riverdale'});
	currentArray.append({'name':'Historic Hoboken Terminal', 'link':'/mosaic/26765', 'city':' Hoboken'});
	currentArray.append({'name':'Storm of 79 Order', 'link':'/mosaic/14001', 'city':' Matawan'});
	currentArray.append({'name':'Ol  Blue Eyes', 'link':'/mosaic/27765', 'city':' Hoboken'});
	currentArray.append({'name':'Oldbridge  Smurfs', 'link':'/mosaic/14518', 'city':' Old Bridge Township'});
	currentArray.append({'name':'The Punisher', 'link':'/mosaic/16172', 'city':' Princeton'});
	currentArray.append({'name':'Circles', 'link':'/mosaic/17537', 'city':' Stafford Township'});
	currentArray.append({'name':'The Key and the Eye', 'link':'/mosaic/17588', 'city':' Monroe Township'});
	currentArray.append({'name':'Do or do not  There is no try', 'link':'/mosaic/17680', 'city':' Sayreville'});
	currentArray.append({'name':'RESWUE Dating', 'link':'/mosaic/19077', 'city':' Cliffside Park'});
	currentArray.append({'name':'Monopoly in Atlantic City  NJ', 'link':'/mosaic/19089', 'city':' Atlantic City'});
	currentArray.append({'name':'Stevens Crest', 'link':'/mosaic/27887', 'city':' Hoboken'});
	currentArray.append({'name':'The Anti-Hero - Simmons', 'link':'/mosaic/18525', 'city':' Milltown'});
	currentArray.append({'name':'Brilliant  Mind', 'link':'/mosaic/26314', 'city':' Princeton'});
	currentArray.append({'name':'Princeton Enlightened', 'link':'/mosaic/16830', 'city':' Princeton'});
	currentArray.append({'name':'Atlantic City Minion', 'link':'/mosaic/18305', 'city':' Atlantic City'});
	currentArray.append({'name':'The Madd Hatter', 'link':'/mosaic/21071', 'city':' Trenton'});
	currentArray.append({'name':'Nostalgic Atlantic City', 'link':'/mosaic/14921', 'city':' Atlantic City'});
	currentArray.append({'name':'Thundercats', 'link':'/mosaic/27038', 'city':' Trenton'});

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
