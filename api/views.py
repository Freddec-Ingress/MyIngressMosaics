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
		
		if m['ref'] == 'Unavailable':
			
			item = Mission(data='{}', title='Fake mission', ref='Unavailable-'+mosaic.ref, mosaic=mosaic, order=m['order'])
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
	
	currentArray.append({'name':'Visit Roseville Fountains', 'link':'/mosaic/408', 'city':'Roseville'});
	currentArray.append({'name':'Coronado Bridge', 'link':'/mosaic/3364', 'city':'Coronado'});
	currentArray.append({'name':'Santa Monica Starburst', 'link':'/mosaic/3367', 'city':'Santa Monica'});
	currentArray.append({'name':'SF Muni Metro Map', 'link':'/mosaic/3368', 'city':'San Francisco'});
	currentArray.append({'name':'Citrus Heights Sights', 'link':'/mosaic/3392', 'city':'Citrus Heights'});
	currentArray.append({'name':'Bay Bridge', 'link':'/mosaic/3399', 'city':'San Francisco'});
	currentArray.append({'name':'Calle 24 - Juri Commons', 'link':'/mosaic/3403', 'city':'San Francisco'});
	currentArray.append({'name':'Fresno County Courthouse Park Mission', 'link':'/mosaic/3431', 'city':'Fresno'});
	currentArray.append({'name':'Glory of the Verdant Cow', 'link':'/mosaic/3433', 'city':'Turlock'});
	currentArray.append({'name':'Mountain View Cemetery', 'link':'/mosaic/3451', 'city':'Oakland'});
	currentArray.append({'name':'Tamalpais View', 'link':'/mosaic/3470', 'city':'Sausalito'});
	currentArray.append({'name':'Tour Downtown Sacramento', 'link':'/mosaic/3472', 'city':'Sacramento'});
	currentArray.append({'name':'Alameda Tour', 'link':'/mosaic/3480', 'city':'Alameda'});
	currentArray.append({'name':'Welcome to Chico State', 'link':'/mosaic/3482', 'city':'Chico'});
	currentArray.append({'name':'Riverside Founder Memorial', 'link':'/mosaic/3496', 'city':'Riverside'});
	currentArray.append({'name':'Explore the area In-N-Outs', 'link':'/mosaic/3501', 'city':'Laguna Niguel'});
	currentArray.append({'name':'Imperial Beach Pier', 'link':'/mosaic/3540', 'city':'Imperial Beach'});
	currentArray.append({'name':'Balboa Mosaic', 'link':'/mosaic/3587', 'city':'Newport Beach'});
	currentArray.append({'name':'Campbell Farmer s Market', 'link':'/mosaic/5935', 'city':'Campbell'});
	currentArray.append({'name':'Point Reyes Shipwreck', 'link':'/mosaic/5943', 'city':'Corte Madera'});
	currentArray.append({'name':'Island Sunset', 'link':'/mosaic/5982', 'city':'Newport Beach'});
	currentArray.append({'name':'San Diego Postcard', 'link':'/mosaic/6220', 'city':'San Diego'});
	currentArray.append({'name':'San Diego Zoo', 'link':'/mosaic/6221', 'city':'San Diego'});
	currentArray.append({'name':'Butterfly Mission', 'link':'/mosaic/6335', 'city':'El Segundo'});
	currentArray.append({'name':'Norh Park Mural', 'link':'/mosaic/6682', 'city':'San Diego'});
	currentArray.append({'name':'Hayward  The Black Hole', 'link':'/mosaic/6809', 'city':'Hayward'});
	currentArray.append({'name':'Sun Leandro', 'link':'/mosaic/6811', 'city':'San Leandro'});
	currentArray.append({'name':'Explore UCSB Campus', 'link':'/mosaic/6836', 'city':'Goleta'});
	currentArray.append({'name':'Downtown Ventura', 'link':'/mosaic/7021', 'city':'Ventura'});
	currentArray.append({'name':'Visalia courthouse', 'link':'/mosaic/7510', 'city':'Visalia'});
	currentArray.append({'name':'Turquoise Butterfly', 'link':'/mosaic/7999', 'city':'Downey'});
	currentArray.append({'name':'Hanford courthouse', 'link':'/mosaic/9178', 'city':'Hanford'});
	currentArray.append({'name':'Polk Street Stroll', 'link':'/mosaic/9250', 'city':'San Francisco'});
	currentArray.append({'name':'King of the Missions - San Luis Rey', 'link':'/mosaic/9312', 'city':'Oceanside'});
	currentArray.append({'name':'Path of the Enlightened', 'link':'/mosaic/9314', 'city':'Huntington Beach'});
	currentArray.append({'name':'Temple City Camellias', 'link':'/mosaic/9323', 'city':'Temple City'});
	currentArray.append({'name':'HB Pier Pressure', 'link':'/mosaic/9405', 'city':'Huntington Beach'});
	currentArray.append({'name':'Hepner Hall - SDSU', 'link':'/mosaic/9780', 'city':'San Diego'});
	currentArray.append({'name':'La Jolla Children s Pool', 'link':'/mosaic/9785', 'city':'San Diego'});
	currentArray.append({'name':'Peninsula Power', 'link':'/mosaic/9917', 'city':'Rancho Palos Verdes'});
	currentArray.append({'name':'Redondo Beach Pier', 'link':'/mosaic/9971', 'city':'Redondo Beach'});
	currentArray.append({'name':'San Mateo County History Museum', 'link':'/mosaic/9993', 'city':'Redwood City'});
	currentArray.append({'name':'Discover Solvang', 'link':'/mosaic/10015', 'city':'Solvang'});
	currentArray.append({'name':'Enlighten the World', 'link':'/mosaic/10019', 'city':'Claremont'});
	currentArray.append({'name':'Monterey Bay Aquarium', 'link':'/mosaic/10051', 'city':'Monterey'});
	currentArray.append({'name':'Paradise Banner', 'link':'/mosaic/10475', 'city':'Paradise'});
	currentArray.append({'name':'The Gryffindor Trio', 'link':'/mosaic/11091', 'city':'Los Angeles'});
	currentArray.append({'name':'Visit Adventureland and Critter Country', 'link':'/mosaic/11302', 'city':'Anaheim'});
	currentArray.append({'name':'Colma', 'link':'/mosaic/11322', 'city':'Daly City'});
	currentArray.append({'name':'Mainstreet U S A', 'link':'/mosaic/11339', 'city':'Anaheim'});
	currentArray.append({'name':'Weeping Angel', 'link':'/mosaic/11365', 'city':'Stanford'});
	currentArray.append({'name':'Explorer of Lakewood', 'link':'/mosaic/11383', 'city':'Lakewood'});
	currentArray.append({'name':'SeaWorld is the Place to Be', 'link':'/mosaic/11451', 'city':'San Diego'});
	currentArray.append({'name':'Municipal Pier Redondo', 'link':'/mosaic/11543', 'city':'Redondo Beach'});
	currentArray.append({'name':'Oceanside Pier Mosaic', 'link':'/mosaic/11552', 'city':'Oceanside'});
	currentArray.append({'name':'Visit Tomorrowland', 'link':'/mosaic/11554', 'city':'Anaheim'});
	currentArray.append({'name':'Catalina Mosaic', 'link':'/mosaic/11714', 'city':'Avalon'});
	currentArray.append({'name':'Ocean Beach Pier', 'link':'/mosaic/11848', 'city':'San Diego'});
	currentArray.append({'name':'Seal Beach Pier Mural', 'link':'/mosaic/12402', 'city':'Seal Beach'});
	currentArray.append({'name':'La Mirada Agricultural History', 'link':'/mosaic/12404', 'city':'Santa Fe Springs'});
	currentArray.append({'name':'Victorian Ferndale Walkabout', 'link':'/mosaic/12412', 'city':'Ferndale'});
	currentArray.append({'name':'Crystal Pier', 'link':'/mosaic/12487', 'city':'San Diego'});
	currentArray.append({'name':'Sunset Cliffs', 'link':'/mosaic/12488', 'city':'San Diego'});
	currentArray.append({'name':'Storming The Beachesl', 'link':'/mosaic/12572', 'city':'Long Beach'});
	currentArray.append({'name':'Explore UC Irvine', 'link':'/mosaic/12881', 'city':'Irvine'});
	currentArray.append({'name':'Capture the NTC Command Center', 'link':'/mosaic/12935', 'city':'San Diego'});
	currentArray.append({'name':'LACoFD Proud Protectors', 'link':'/mosaic/12999', 'city':'Bellflower'});
	currentArray.append({'name':'Outgress', 'link':'/mosaic/13001', 'city':'San Diego'});
	currentArray.append({'name':'PV Resistance', 'link':'/mosaic/13005', 'city':'Los Angeles'});
	currentArray.append({'name':'Fabulous Hillcrest', 'link':'/mosaic/13245', 'city':'San Diego'});
	currentArray.append({'name':'Visit Fantasy Land', 'link':'/mosaic/13834', 'city':'Anaheim'});
	currentArray.append({'name':'Well Qualified to Represent the LBC', 'link':'/mosaic/14045', 'city':'Long Beach'});
	currentArray.append({'name':'Wienermobile', 'link':'/mosaic/14056', 'city':'Los Angeles'});
	currentArray.append({'name':'Discover Lake Balboa Park (SFV  CA)', 'link':'/mosaic/14278', 'city':'Los Angeles'});
	currentArray.append({'name':'San Mateo', 'link':'/mosaic/14323', 'city':'San Mateo'});
	currentArray.append({'name':'Night at the Drive-In', 'link':'/mosaic/14420', 'city':'Westminster'});
	currentArray.append({'name':'Mission Dolores', 'link':'/mosaic/14710', 'city':'San Francisco'});
	currentArray.append({'name':'Tour of Oroville', 'link':'/mosaic/14770', 'city':'Oroville'});
	currentArray.append({'name':'Bakersfield - All American City', 'link':'/mosaic/14872', 'city':'Bakersfield'});
	currentArray.append({'name':'Capture the Whaley House', 'link':'/mosaic/14917', 'city':'San Diego'});
	currentArray.append({'name':'Petaluma Riviera', 'link':'/mosaic/15314', 'city':'Petaluma'});
	currentArray.append({'name':'Octopus At Pixels', 'link':'/mosaic/15870', 'city':'Riverside'});
	currentArray.append({'name':'Explore Little Tokyo [Shō-tōkyō]', 'link':'/mosaic/15871', 'city':'Los Angeles'});
	currentArray.append({'name':'LLU Vision 2020', 'link':'/mosaic/15872', 'city':'Loma Linda'});
	currentArray.append({'name':'SFV Ingress Ponies', 'link':'/mosaic/15873', 'city':'Los Angeles'});
	currentArray.append({'name':'Humboldt Fog', 'link':'/mosaic/16394', 'city':'Fortuna'});
	currentArray.append({'name':'Downtown Chico Adventure', 'link':'/mosaic/16407', 'city':'Chico'});
	currentArray.append({'name':'Verdant Storm of Enlightenment', 'link':'/mosaic/16489', 'city':'San Diego'});
	currentArray.append({'name':'Fisherman s Wharf', 'link':'/mosaic/16592', 'city':'Monterey'});
	currentArray.append({'name':'Mission San Luis Obispo', 'link':'/mosaic/17081', 'city':'San Luis Obispo'});
	currentArray.append({'name':'rancho banner', 'link':'/mosaic/17121', 'city':'Rancho Cordova'});
	currentArray.append({'name':'5k at L B J', 'link':'/mosaic/17245', 'city':'Orick'});
	currentArray.append({'name':'San Ysidro Mural', 'link':'/mosaic/17412', 'city':'San Diego'});
	currentArray.append({'name':'In Memory of Officer Galvez', 'link':'/mosaic/17730', 'city':'Downey'});
	currentArray.append({'name':'Betty s Glasses', 'link':'/mosaic/17799', 'city':'Santa Clara'});
	currentArray.append({'name':'Explore the Coachella Valley', 'link':'/mosaic/18216', 'city':'Palm Springs'});
	currentArray.append({'name':'San José Grand Voyage V', 'link':'/mosaic/18246', 'city':'San Jose'});
	currentArray.append({'name':'Explore Palm Springs', 'link':'/mosaic/18351', 'city':'Palm Springs'});
	currentArray.append({'name':'Morro Rock', 'link':'/mosaic/18427', 'city':'Morro Bay'});
	currentArray.append({'name':'Historical Anaheim Packing House', 'link':'/mosaic/18445', 'city':'Anaheim'});
	currentArray.append({'name':'Who s got the AXE - 2', 'link':'/mosaic/18507', 'city':'Berkeley'});
	currentArray.append({'name':'Martinez Regional Shoreline', 'link':'/mosaic/18565', 'city':'Martinez'});
	currentArray.append({'name':'May the force be with MV', 'link':'/mosaic/18568', 'city':'Mountain View'});
	currentArray.append({'name':'Well here we are  Pismo Beach', 'link':'/mosaic/18595', 'city':'Pismo Beach'});
	currentArray.append({'name':'Chicano Park Mural', 'link':'/mosaic/18672', 'city':'San Diego'});
	currentArray.append({'name':'Fine Arts Museums of San Francisco', 'link':'/mosaic/18737', 'city':'San Francisco'});
	currentArray.append({'name':'Arcata historic tour series', 'link':'/mosaic/19226', 'city':'Arcata'});
	currentArray.append({'name':'Get in the van BRO', 'link':'/mosaic/19247', 'city':'Whittier'});
	currentArray.append({'name':'Learn by Doing', 'link':'/mosaic/19254', 'city':'San Luis Obispo'});
	currentArray.append({'name':'Paramount Iceland', 'link':'/mosaic/19261', 'city':'Paramount'});
	currentArray.append({'name':'Santa Cruz Starburst', 'link':'/mosaic/19406', 'city':'Santa Cruz'});
	currentArray.append({'name':'KermiWan Kenobi', 'link':'/mosaic/19468', 'city':'Corona'});
	currentArray.append({'name':'Medals Series - CA', 'link':'/mosaic/19501', 'city':'Alameda'});
	currentArray.append({'name':'Jewel of the Missions', 'link':'/mosaic/19692', 'city':'San Juan Capistrano'});
	currentArray.append({'name':'Sunset Wild Run', 'link':'/mosaic/19878', 'city':'Los Angeles'});
	currentArray.append({'name':'Wilshire Facts', 'link':'/mosaic/19879', 'city':'Los Angeles'});
	currentArray.append({'name':'Sapphire Cyborg Components', 'link':'/mosaic/20195', 'city':'Norwalk'});
	currentArray.append({'name':'Visit Buena Vista St and Hollywood Land', 'link':'/mosaic/20249', 'city':'Anaheim'});
	currentArray.append({'name':'Newport Pier in all its Bluety', 'link':'/mosaic/20454', 'city':'Newport Beach'});
	currentArray.append({'name':'Tall Ships of Dana Point', 'link':'/mosaic/20458', 'city':'Dana Point'});
	currentArray.append({'name':'Black Cat', 'link':'/mosaic/20516', 'city':'Atascadero'});
	currentArray.append({'name':'Visit Downtown disney', 'link':'/mosaic/20534', 'city':'Anaheim'});
	currentArray.append({'name':'Visit Paradise Pier', 'link':'/mosaic/20535', 'city':'Anaheim'});
	currentArray.append({'name':'Haybalers Of Hollister', 'link':'/mosaic/20567', 'city':'Hollister'});
	currentArray.append({'name':'There s Something About', 'link':'/mosaic/20618', 'city':'Torrance'});
	currentArray.append({'name':'Plaza Mexico', 'link':'/mosaic/20795', 'city':'Lynwood'});
	currentArray.append({'name':'Memorial To Ghost Ship', 'link':'/mosaic/20810', 'city':'Oakland'});
	currentArray.append({'name':'Bueller    Bueller    Bueller', 'link':'/mosaic/20935', 'city':'Long Beach'});
	currentArray.append({'name':'NOHO Circus Liquor', 'link':'/mosaic/21080', 'city':'Los Angeles'});
	currentArray.append({'name':'Taquero Mucho', 'link':'/mosaic/21362', 'city':'Los Angeles'});
	currentArray.append({'name':'Mothers Day - SD 2017', 'link':'/mosaic/21385', 'city':'El Cajon'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Park B', 'link':'/mosaic/21933', 'city':'San Diego'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Pasadena  CA', 'link':'/mosaic/22128', 'city':'Pasadena'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart LA #2', 'link':'/mosaic/22406', 'city':'Los Angeles'});
	currentArray.append({'name':'One if by land  and two if by sea', 'link':'/mosaic/22524', 'city':'Cerritos'});
	currentArray.append({'name':'Stearns Wharf', 'link':'/mosaic/22528', 'city':'Santa Barbara'});
	currentArray.append({'name':'Ferry Building', 'link':'/mosaic/22961', 'city':'San Francisco'});
	currentArray.append({'name':'Alamo Square Painted Ladies', 'link':'/mosaic/22966', 'city':'San Francisco'});
	currentArray.append({'name':'Saint Raphael the Archangel', 'link':'/mosaic/23042', 'city':'San Rafael'});
	currentArray.append({'name':'The Milpitas Monster', 'link':'/mosaic/23480', 'city':'Milpitas'});
	currentArray.append({'name':'UCSC Campus Tour', 'link':'/mosaic/23483', 'city':'Santa Cruz'});
	currentArray.append({'name':'Ghost Heart', 'link':'/mosaic/23570', 'city':'Oakland'});
	currentArray.append({'name':'Sideways Mission Series', 'link':'/mosaic/23796', 'city':'Temecula'});
	currentArray.append({'name':'Who s got the AXE', 'link':'/mosaic/23867', 'city':'Stanford'});
	currentArray.append({'name':'Irvine  The Final Frontier', 'link':'/mosaic/23950', 'city':'Irvine'});
	currentArray.append({'name':'Resistance is not Futile in Irvine', 'link':'/mosaic/23951', 'city':'Irvine'});
	currentArray.append({'name':'Unity Through Enlightenment', 'link':'/mosaic/24138', 'city':'Modesto'});
	currentArray.append({'name':'Solar Eclipse-Red', 'link':'/mosaic/24207', 'city':'La Mirada'});
	currentArray.append({'name':'Memorial Day – SD 2017', 'link':'/mosaic/24217', 'city':'San Diego'});
	currentArray.append({'name':'Merced Theatre at Night', 'link':'/mosaic/24302', 'city':'Merced'});
	currentArray.append({'name':'Hamilton Air Force Base', 'link':'/mosaic/24380', 'city':'Novato'});
	currentArray.append({'name':'The Walter Pyramid', 'link':'/mosaic/24575', 'city':'Long Beach'});
	currentArray.append({'name':'Solar Eclipse-Water', 'link':'/mosaic/24585', 'city':'Buena Park'});
	currentArray.append({'name':'Fillmore Jazz Sessions', 'link':'/mosaic/25198', 'city':'San Francisco'});
	currentArray.append({'name':'Dance your way around Old Town', 'link':'/mosaic/25514', 'city':'San Diego'});
	currentArray.append({'name':'4th of July', 'link':'/mosaic/25520', 'city':'Coronado'});
	currentArray.append({'name':'Father’s Day – SD2017', 'link':'/mosaic/25542', 'city':'San Diego'});
	currentArray.append({'name':'Pier Cafe', 'link':'/mosaic/25581', 'city':'San Diego'});
	currentArray.append({'name':'Porter Squiggle', 'link':'/mosaic/25582', 'city':'Santa Cruz'});
	currentArray.append({'name':'See the Sea Turtles', 'link':'/mosaic/25589', 'city':'Long Beach'});
	currentArray.append({'name':'SD Comic-Con', 'link':'/mosaic/25762', 'city':'San Diego'});
	currentArray.append({'name':'Camp Pendleton Mosaic', 'link':'/mosaic/26009', 'city':'Oceanside'});
	currentArray.append({'name':'Encinitas Sunset', 'link':'/mosaic/26657', 'city':'Encinitas'});
	currentArray.append({'name':'Fallbrook The Avocado Capital', 'link':'/mosaic/26658', 'city':'Fallbrook'});
	currentArray.append({'name':'HB Solar Eclipse', 'link':'/mosaic/26660', 'city':'Huntington Beach'});
	currentArray.append({'name':'Darkside', 'link':'/mosaic/27252', 'city':'Mountain View'});
	currentArray.append({'name':'Zen Frog', 'link':'/mosaic/27342', 'city':'San Leandro'});

	for item in currentArray:
		
		results = Mosaic.objects.filter(title=item['name'])
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
