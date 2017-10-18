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
	
	currentArray.append({'name':'Water Works  Glyph', 'link':'/mosaic/23914', 'city':' Tampa'});
	currentArray.append({'name':'Turkey Creek Tour', 'link':'/mosaic/3707', 'city':' Malabar'});
	currentArray.append({'name':'Mosaic SeaWorld', 'link':'/mosaic/4105', 'city':' Orlando'});
	currentArray.append({'name':'Epcot Mission Banner', 'link':'/mosaic/4148', 'city':' Epcot'});
	currentArray.append({'name':'Lake City', 'link':'/mosaic/4763', 'city':' Lake City'});
	currentArray.append({'name':'Tour Historic Downtown', 'link':'/mosaic/5960', 'city':' Melbourne'});
	currentArray.append({'name':'Florida Tech', 'link':'/mosaic/6040', 'city':' Melbourne'});
	currentArray.append({'name':'Tour of Malabar Park', 'link':'/mosaic/8639', 'city':' Malabar'});
	currentArray.append({'name':'Crandon Marina', 'link':'/mosaic/8909', 'city':' Key Biscayne'});
	currentArray.append({'name':'Hack the Camp', 'link':'/mosaic/9167', 'city':' Starke'});
	currentArray.append({'name':'Unique Frog Token', 'link':'/mosaic/10172', 'city':' Tampa'});
	currentArray.append({'name':'WINTER GARDEN CITY HALL ENL', 'link':'/mosaic/12112', 'city':' Winter Garden'});
	currentArray.append({'name':'A 1920s Day on the Pithlachascotee River', 'link':'/mosaic/12146', 'city':' New Port Richey'});
	currentArray.append({'name':'Cute Frog', 'link':'/mosaic/12149', 'city':' Fort Lauderdale'});
	currentArray.append({'name':'TARDIS at Santa Fe College', 'link':'/mosaic/12620', 'city':' Gainesville'});
	currentArray.append({'name':'Sarasota Bayfront Mission Series', 'link':'/mosaic/12981', 'city':' Sarasota'});
	currentArray.append({'name':'Pier 60', 'link':'/mosaic/13860', 'city':' Clearwater'});
	currentArray.append({'name':'Star Gazing at the Pier', 'link':'/mosaic/14325', 'city':' Saint Petersburg'});
	currentArray.append({'name':'Meal Time', 'link':'/mosaic/15031', 'city':' Palm Coast'});
	currentArray.append({'name':'Ybor City Mural Part 1', 'link':'/mosaic/15054', 'city':' Tampa'});
	currentArray.append({'name':'Magic Kingdom', 'link':'/mosaic/15258', 'city':' Orlando'});
	currentArray.append({'name':'MissionDay Miami - (13-11-2016)', 'link':'/mosaic/15805', 'city':' Miami'});
	currentArray.append({'name':'JU Dolphins', 'link':'/mosaic/16902', 'city':' Jacksonville'});
	currentArray.append({'name':'Fort Meade s Very Own', 'link':'/mosaic/16977', 'city':' Fort Meade'});
	currentArray.append({'name':'The Doctors Regeneration', 'link':'/mosaic/19212', 'city':' Dade City'});
	currentArray.append({'name':'Crystal River Manatee HACK', 'link':'/mosaic/19575', 'city':' Homosassa'});
	currentArray.append({'name':'Surf Shops of Florida', 'link':'/mosaic/21265', 'city':' Tallahassee'});
	currentArray.append({'name':'Watchful Eye of Sumter County', 'link':'/mosaic/21322', 'city':' Bushnell'});
	currentArray.append({'name':'Ybor City Hacks - Mural Missions', 'link':'/mosaic/21400', 'city':' Tampa'});
	currentArray.append({'name':'Collier Parkway Area Mission banner', 'link':'/mosaic/22116', 'city':' Land O’ Lakes'});
	currentArray.append({'name':'Pinky Tribute - Hack The Flock', 'link':'/mosaic/22482', 'city':' Tampa'});
	currentArray.append({'name':'Halloween in Hernando Haunts   Hacks', 'link':'/mosaic/22701', 'city':' Brooksville'});
	currentArray.append({'name':'Hacking St Leo University Campus Banner', 'link':'/mosaic/22702', 'city':' San Antonio'});
	currentArray.append({'name':'Salute - Magnus Reawakens (Tribute Banner)', 'link':'/mosaic/22901', 'city':' Ocala'});
	currentArray.append({'name':'Green Cay Wetlands', 'link':'/mosaic/22904', 'city':' Boynton Beach'});
	currentArray.append({'name':'Papa s Night Out', 'link':'/mosaic/23016', 'city':' Fort Myers'});
	currentArray.append({'name':'Finding Floral City - Moonrise Resort', 'link':'/mosaic/23348', 'city':' Brooksville'});
	currentArray.append({'name':'Solar Walk', 'link':'/mosaic/23404', 'city':' Gainesville'});
	currentArray.append({'name':'The Irony of Illumination', 'link':'/mosaic/24137', 'city':' Odessa'});
	currentArray.append({'name':'Disney Springs TRex', 'link':'/mosaic/24644', 'city':' Orlando'});
	currentArray.append({'name':'Disney Springs', 'link':'/mosaic/24645', 'city':' Orlando'});
	currentArray.append({'name':'My Precious', 'link':'/mosaic/24837', 'city':' Lutz'});
	currentArray.append({'name':'Legoland ~ There s no otter place like it', 'link':'/mosaic/24839', 'city':' Winter Haven'});
	currentArray.append({'name':'Natural Surroundings of Boyd Hill Preserve', 'link':'/mosaic/24842', 'city':' Saint Petersburg'});
	currentArray.append({'name':'DHS Kissimmee', 'link':'/mosaic/25918', 'city':' Kissimmee'});
	currentArray.append({'name':'Honeymoon Causeway', 'link':'/mosaic/26564', 'city':' Dunedin'});
	currentArray.append({'name':'Hack Epcot Futureworld', 'link':'/mosaic/27619', 'city':' Orlando'});
	currentArray.append({'name':'Zombie Hunt', 'link':'/mosaic/12863', 'city':' Lutz'});
	currentArray.append({'name':'Hack the Dead', 'link':'/mosaic/18821', 'city':' Jacksonville'});
	currentArray.append({'name':'Tour de Bartow', 'link':'/mosaic/20487', 'city':' Bartow'});
	currentArray.append({'name':'Rivers of Southwest Florida', 'link':'/mosaic/1590', 'city':' Arcadia'});
	currentArray.append({'name':'Enlightened Dragons LW', 'link':'/mosaic/3344', 'city':' Lake Worth'});
	currentArray.append({'name':'Downtown Jax', 'link':'/mosaic/3503', 'city':' Jacksonville'});
	currentArray.append({'name':'Mosaic Gardens', 'link':'/mosaic/3602', 'city':' Tampa'});
	currentArray.append({'name':'Temple Terrace Mosaic', 'link':'/mosaic/4106', 'city':' Tampa'});
	currentArray.append({'name':'Great to Be a Gator', 'link':'/mosaic/4975', 'city':' Gainesville'});
	currentArray.append({'name':'A Carousel of Dreams - Tampa Florida', 'link':'/mosaic/6233', 'city':' Tampa'});
	currentArray.append({'name':'Orlando Obsidian', 'link':'/mosaic/7139', 'city':' Orlando'});
	currentArray.append({'name':'MissionDay Orlando', 'link':'/mosaic/7142', 'city':' Orlando'});
	currentArray.append({'name':'Paradise on Pensacola Beach', 'link':'/mosaic/7469', 'city':' Gulf Breeze'});
	currentArray.append({'name':'Castillo de San Marcos  The Fort', 'link':'/mosaic/7728', 'city':' St. Augustine'});
	currentArray.append({'name':'Magical Mouse Memories', 'link':'/mosaic/8706', 'city':' Orlando'});
	currentArray.append({'name':'CWGDN', 'link':'/mosaic/8914', 'city':' Winter Garden'});
	currentArray.append({'name':'Downtown Sanford', 'link':'/mosaic/9043', 'city':' Sanford'});
	currentArray.append({'name':'Florida State University Banner', 'link':'/mosaic/9091', 'city':' Tallahassee'});
	currentArray.append({'name':'Guardian of The Enlightened', 'link':'/mosaic/9159', 'city':' Hollywood'});
	currentArray.append({'name':'Jax Zoo', 'link':'/mosaic/9293', 'city':' Jacksonville'});
	currentArray.append({'name':'Historic Cocoa Village', 'link':'/mosaic/9567', 'city':' Cocoa'});
	currentArray.append({'name':'Jax Westside', 'link':'/mosaic/9593', 'city':' Jacksonville'});
	currentArray.append({'name':'NAS JAX', 'link':'/mosaic/9604', 'city':' Jacksonville'});
	currentArray.append({'name':'River Cities', 'link':'/mosaic/9614', 'city':' Miami'});
	currentArray.append({'name':'WG OBSIDIAN BANNER', 'link':'/mosaic/9633', 'city':' Winter Garden'});
	currentArray.append({'name':'partyparrot', 'link':'/mosaic/9982', 'city':' Tallahassee'});
	currentArray.append({'name':'Barcodes Of Jax', 'link':'/mosaic/9995', 'city':' Jacksonville'});
	currentArray.append({'name':'Clearwater Sandcastle', 'link':'/mosaic/10011', 'city':' Clearwater'});
	currentArray.append({'name':'Downtown Sarasota Mosaic', 'link':'/mosaic/10017', 'city':' Sarasota'});
	currentArray.append({'name':'Exploring Disney s Animal Kingdom', 'link':'/mosaic/10022', 'city':' Kissimmee'});
	currentArray.append({'name':'Lord of the Green', 'link':'/mosaic/10040', 'city':' Miami'});
	currentArray.append({'name':'Wickham Park II', 'link':'/mosaic/10115', 'city':' Melbourne'});
	currentArray.append({'name':'Downtown St  Petersburg', 'link':'/mosaic/10753', 'city':' Saint Petersburg'});
	currentArray.append({'name':'MDC Kendall Campus', 'link':'/mosaic/11341', 'city':' Miami'});
	currentArray.append({'name':'Horse Capital', 'link':'/mosaic/11550', 'city':' Ocala'});
	currentArray.append({'name':'Sarasota Beach Mosaic', 'link':'/mosaic/11711', 'city':' Sarasota'});
	currentArray.append({'name':'Hudson Trek', 'link':'/mosaic/12067', 'city':' Hudson'});
	currentArray.append({'name':'Get HIPP', 'link':'/mosaic/12105', 'city':' Gainesville'});
	currentArray.append({'name':'Alligator Eyeshine', 'link':'/mosaic/12187', 'city':' Gainesville'});
	currentArray.append({'name':'Shivan Dragon', 'link':'/mosaic/12427', 'city':' Gainesville'});
	currentArray.append({'name':'Miami Lakes Banner', 'link':'/mosaic/12916', 'city':' Hialeah'});
	currentArray.append({'name':'Mosaic Pier Venice', 'link':'/mosaic/13799', 'city':' Venice'});
	currentArray.append({'name':'Key West Cat s Eye', 'link':'/mosaic/14054', 'city':' Key West'});
	currentArray.append({'name':'3rd Dimension Kitty', 'link':'/mosaic/14720', 'city':' Miami'});
	currentArray.append({'name':'Bridge Of Lions   The Lion', 'link':'/mosaic/14859', 'city':' St. Augustine'});
	currentArray.append({'name':'Farm Around Town', 'link':'/mosaic/15022', 'city':' Flagler Beach'});
	currentArray.append({'name':'Flagler Beach Shark Attack Mural', 'link':'/mosaic/15027', 'city':' Flagler Beach'});
	currentArray.append({'name':'Surf A1A', 'link':'/mosaic/15028', 'city':' St. Augustine'});
	currentArray.append({'name':'Miami Beach Postcard', 'link':'/mosaic/15818', 'city':' Miami Beach'});
	currentArray.append({'name':'Night of Lights', 'link':'/mosaic/16416', 'city':' St. Augustine'});
	currentArray.append({'name':'Quilt The Harn', 'link':'/mosaic/16978', 'city':' Gainesville'});
	currentArray.append({'name':'MD  Jacksonville', 'link':'/mosaic/18109', 'city':' Jacksonville Beach'});
	currentArray.append({'name':'Palm Beach Gardens Tour', 'link':'/mosaic/18433', 'city':' Palm Beach Gardens'});
	currentArray.append({'name':'Ybor City Mural 3', 'link':'/mosaic/18489', 'city':' Tampa'});
	currentArray.append({'name':'Emerald City Hack', 'link':'/mosaic/18522', 'city':' Lake Worth'});
	currentArray.append({'name':'Kissimmee', 'link':'/mosaic/18589', 'city':' Kissimmee'});
	currentArray.append({'name':'Vape Queen Mural', 'link':'/mosaic/18590', 'city':' Fort Lauderdale'});
	currentArray.append({'name':'Jax Swagger', 'link':'/mosaic/18822', 'city':' Jacksonville'});
	currentArray.append({'name':'Fallout Banner Mission', 'link':'/mosaic/19029', 'city':' Tallahassee'});
	currentArray.append({'name':'in a series Dade City Bug Jammed', 'link':'/mosaic/19221', 'city':' Dade City'});
	currentArray.append({'name':'Wynwood Mission', 'link':'/mosaic/19280', 'city':' Miami'});
	currentArray.append({'name':'Moon Chiller', 'link':'/mosaic/19467', 'city':' Lehigh Acres'});
	currentArray.append({'name':'Evergreen Terrace', 'link':'/mosaic/19798', 'city':' Miami'});
	currentArray.append({'name':'Enlightened Vader', 'link':'/mosaic/19908', 'city':' Tallahassee'});
	currentArray.append({'name':'Where Is Musto', 'link':'/mosaic/20126', 'city':' Tallahassee'});
	currentArray.append({'name':'Remembering Columbia', 'link':'/mosaic/20127', 'city':' Tallahassee'});
	currentArray.append({'name':'Everglades Vista', 'link':'/mosaic/20424', 'city':' Homestead'});
	currentArray.append({'name':'ZHills area hacks for a cool banner', 'link':'/mosaic/21065', 'city':' Zephyrhills'});
	currentArray.append({'name':'Hack  Cap  Mod Lutz Downtown Area', 'link':'/mosaic/21108', 'city':' Lutz'});
	currentArray.append({'name':'Boca Grande Greening', 'link':'/mosaic/21389', 'city':' Boca Grande'});
	currentArray.append({'name':'Green Face', 'link':'/mosaic/21391', 'city':' Punta Gorda'});
	currentArray.append({'name':'Shrooming Greenery', 'link':'/mosaic/21392', 'city':' Punta Gorda'});
	currentArray.append({'name':'Westside Greening', 'link':'/mosaic/21394', 'city':' Venice'});
	currentArray.append({'name':'Nebraska Ave North Trek Acoss Town', 'link':'/mosaic/21402', 'city':' Tampa'});
	currentArray.append({'name':'The Biltmore Hotel', 'link':'/mosaic/21705', 'city':' Miami'});
	currentArray.append({'name':'Deering Estate Sunrise', 'link':'/mosaic/21706', 'city':' Miami'});
	currentArray.append({'name':'Devastate Downtown Dunedin', 'link':'/mosaic/22571', 'city':' Dunedin'});
	currentArray.append({'name':'Cruisin  Lake Monroe', 'link':'/mosaic/23145', 'city':' DeBary'});
	currentArray.append({'name':'Power Of Two', 'link':'/mosaic/23424', 'city':' Gainesville'});
	currentArray.append({'name':'Free Flight', 'link':'/mosaic/23982', 'city':' Orange City'});
	currentArray.append({'name':'Clermont Tour of the City', 'link':'/mosaic/24405', 'city':' Clermont'});
	currentArray.append({'name':'Raging Bulls On Parade', 'link':'/mosaic/24478', 'city':' West Palm Beach'});
	currentArray.append({'name':'Brown  Pelican', 'link':'/mosaic/24544', 'city':' Port Orange'});
	currentArray.append({'name':'Fear and Loathing Rick   Morty Style', 'link':'/mosaic/24677', 'city':' Winter Haven'});
	currentArray.append({'name':'Crucible', 'link':'/mosaic/24757', 'city':' Vero Beach'});
	currentArray.append({'name':'Melbourne Is Grumpy', 'link':'/mosaic/24799', 'city':' Melbourne'});
	currentArray.append({'name':'The Cake is not a Pie', 'link':'/mosaic/24836', 'city':' New Port Richey'});
	currentArray.append({'name':'STYLO', 'link':'/mosaic/24841', 'city':' Spring Hill'});
	currentArray.append({'name':'The Greatest Show on Earth', 'link':'/mosaic/24955', 'city':' Sarasota'});
	currentArray.append({'name':'Beautiful Florida - The Winter Playground of the Nation - Post Card', 'link':'/mosaic/25271', 'city':' Inverness'});
	currentArray.append({'name':'Ocala ~ The Equestrian County', 'link':'/mosaic/25272', 'city':' Ocala'});
	currentArray.append({'name':'Dead Man s Hand', 'link':'/mosaic/25532', 'city':' Cape Coral'});
	currentArray.append({'name':'Feeling Fruity', 'link':'/mosaic/25543', 'city':' Fort Myers'});
	currentArray.append({'name':'The Professional', 'link':'/mosaic/25603', 'city':' Fort Myers'});
	currentArray.append({'name':'UF Then  amp  Now', 'link':'/mosaic/25611', 'city':' Gainesville'});
	currentArray.append({'name':'Against the odds', 'link':'/mosaic/26190', 'city':' Port St. Lucie'});
	currentArray.append({'name':'Disney s Animal Kingdom Portal Tour', 'link':'/mosaic/26295', 'city':' Kissimmee'});
	currentArray.append({'name':'Whale Island', 'link':'/mosaic/26721', 'city':' Fort Myers'});
	currentArray.append({'name':'Pineapple Catfish', 'link':'/mosaic/26852', 'city':' Fort Myers'});
	currentArray.append({'name':'Gainesville Then and Now', 'link':'/mosaic/27426', 'city':' Gainesville'});
	currentArray.append({'name':'Get out of your car', 'link':'/mosaic/27428', 'city':' Fort Myers'});
	currentArray.append({'name':'MD  Tallahassee', 'link':'/mosaic/27730', 'city':' Tallahassee'});
	currentArray.append({'name':'PRide Lake Eola', 'link':'/mosaic/27869', 'city':' Orlando'});
	currentArray.append({'name':'Palm Coast Enlightened Missions', 'link':'/mosaic/20817', 'city':' Palm Coast'});
	currentArray.append({'name':'Tally Series Mission', 'link':'/mosaic/3339', 'city':' Tallahassee'});
	currentArray.append({'name':'Dunedin Postcard Mural', 'link':'/mosaic/3459', 'city':' Dunedin'});
	currentArray.append({'name':'Tampa Mural Mosaic Mission', 'link':'/mosaic/3603', 'city':' Tampa'});
	currentArray.append({'name':'RIP Robin W SFR Tribute', 'link':'/mosaic/4047', 'city':' Fort Lauderdale'});
	currentArray.append({'name':'The Perfection of Lake Eola', 'link':'/mosaic/4066', 'city':' Orlando'});
	currentArray.append({'name':'Jacksonville Beach  FL -- Beach Walk Skyline', 'link':'/mosaic/4069', 'city':' Jacksonville Beach'});
	currentArray.append({'name':'Bluefire Universal Studios Tour', 'link':'/mosaic/4133', 'city':' Orlando'});
	currentArray.append({'name':'Epcot Tour', 'link':'/mosaic/4146', 'city':' Epcot'});
	currentArray.append({'name':'Disney Hollywood Studios', 'link':'/mosaic/5483', 'city':' Delray Beach'});
	currentArray.append({'name':'Explore Melbourne', 'link':'/mosaic/5618', 'city':' Melbourne'});
	currentArray.append({'name':'Pensacola Five Flags', 'link':'/mosaic/7467', 'city':' Pensacola'});
	currentArray.append({'name':'Portaling Palafox', 'link':'/mosaic/7468', 'city':' Pensacola'});
	currentArray.append({'name':'Orinoco', 'link':'/mosaic/7596', 'city':' Miami'});
	currentArray.append({'name':'Ybor Square', 'link':'/mosaic/8470', 'city':' Tampa'});
	currentArray.append({'name':'Delray Bang District', 'link':'/mosaic/8929', 'city':' Delray Beach'});
	currentArray.append({'name':'SF Mission Series Down Town Hack', 'link':'/mosaic/9033', 'city':' Delray Beach'});
	currentArray.append({'name':'Explore Palm Bay', 'link':'/mosaic/9067', 'city':' Palm Bay'});
	currentArray.append({'name':'Pinellas Dawg Pound', 'link':'/mosaic/9511', 'city':' Pinellas Park'});
	currentArray.append({'name':'Lake Eola XM Hack', 'link':'/mosaic/9751', 'city':' Orlando'});
	currentArray.append({'name':'Under the Moon SFR', 'link':'/mosaic/10623', 'city':' Fort Lauderdale'});
	currentArray.append({'name':'Path of the Gator Series', 'link':'/mosaic/11346', 'city':' Gainesville'});
	currentArray.append({'name':'Downtown Tampa', 'link':'/mosaic/11464', 'city':' Tampa'});
	currentArray.append({'name':'Blue Christmas', 'link':'/mosaic/15881', 'city':' Fort Lauderdale'});
	currentArray.append({'name':'Sunset Banner Drive n Walk', 'link':'/mosaic/16534', 'city':' West Palm Beach'});
	currentArray.append({'name':'ENL #Harambe Mission Day Jax', 'link':'/mosaic/18102', 'city':' Ponte Vedra Beach'});
	currentArray.append({'name':'Business Cat Tribute Banner', 'link':'/mosaic/18112', 'city':' Atlantic Beach'});
	currentArray.append({'name':'Lion in the Busch', 'link':'/mosaic/18455', 'city':' Tampa'});
	currentArray.append({'name':'Historical Florida Citrus Tower', 'link':'/mosaic/18659', 'city':' Clermont'});
	currentArray.append({'name':'WPB Beer Garden Girl', 'link':'/mosaic/19090', 'city':' West Palm Beach'});
	currentArray.append({'name':'El Jobeano El Greeno', 'link':'/mosaic/21390', 'city':' Port Charlotte'});
	currentArray.append({'name':'Swallowing Green', 'link':'/mosaic/21393', 'city':' Port Charlotte'});
	currentArray.append({'name':'Joyfully Jerking', 'link':'/mosaic/21561', 'city':' Fort Myers'});
	currentArray.append({'name':'Delray Beach', 'link':'/mosaic/22403', 'city':' Delray Beach'});
	currentArray.append({'name':'The Face Off', 'link':'/mosaic/22692', 'city':' Palm Beach Gardens'});
	currentArray.append({'name':'Orange You Glad To Be A Frog', 'link':'/mosaic/23663', 'city':' Naples'});
	currentArray.append({'name':'Kravis Center', 'link':'/mosaic/24743', 'city':' West Palm Beach'});
	currentArray.append({'name':'History - Inverness Florida was Tompkinsville in 1860 s', 'link':'/mosaic/24838', 'city':' Inverness'});
	currentArray.append({'name':'Veterans Dedication Trip', 'link':'/mosaic/24959', 'city':' Port St. Lucie'});
	currentArray.append({'name':'Path of Truth', 'link':'/mosaic/25620', 'city':' Gainesville'});
	currentArray.append({'name':'Graffiti Wolf', 'link':'/mosaic/25628', 'city':' Cape Coral'});
	currentArray.append({'name':'Juno The Way To Jupiter', 'link':'/mosaic/25630', 'city':' North Palm Beach'});
	currentArray.append({'name':'The Dark Side of Brevard', 'link':'/mosaic/25703', 'city':' Palm Bay'});
	currentArray.append({'name':'ANCHORS', 'link':'/mosaic/26116', 'city':' Fort Pierce'});
	currentArray.append({'name':'Eyes on the Diamond', 'link':'/mosaic/26690', 'city':' Fort Myers'});
	currentArray.append({'name':'Daytona ABC Mission', 'link':'/mosaic/5600', 'city':' Daytona Beach'});
	currentArray.append({'name':'Oaklawn Cemetery alphabet game', 'link':'/mosaic/21166', 'city':' Tampa'});
	currentArray.append({'name':'Miami Mission Series', 'link':'/mosaic/3581', 'city':' Miami'});
	currentArray.append({'name':'The Orlando Eye', 'link':'/mosaic/4131', 'city':' Orlando'});
	currentArray.append({'name':'Disney Epcot Park', 'link':'/mosaic/9046', 'city':' Delray Beach'});
	currentArray.append({'name':'Historic Delray District', 'link':'/mosaic/9199', 'city':' Delray Beach'});
	currentArray.append({'name':'Melting Watch', 'link':'/mosaic/11374', 'city':' Saint Petersburg'});
	currentArray.append({'name':'Amway Center', 'link':'/mosaic/16666', 'city':' Orlando'});
	currentArray.append({'name':'Miami Pride 2017', 'link':'/mosaic/18794', 'city':' Miami Beach'});
	currentArray.append({'name':'Conquer   Capture at Calvary - Savannah Cemetery Tribute Mission Banner', 'link':'/mosaic/23065', 'city':' Clearwater'});
	currentArray.append({'name':'Manhattan in Miami', 'link':'/mosaic/3582', 'city':' Miami'});
	currentArray.append({'name':'Bluefire IOA Tour', 'link':'/mosaic/3590', 'city':' Orlando'});
	currentArray.append({'name':'Dr  Phillips Center for the Performing Arts', 'link':'/mosaic/4135', 'city':' Orlando'});
	currentArray.append({'name':'Orlando The City Beautiful Mission', 'link':'/mosaic/7141', 'city':' Orlando'});
	currentArray.append({'name':'A Way of Life in Lakeland', 'link':'/mosaic/8721', 'city':' Lakeland'});
	currentArray.append({'name':'Reenactment at Sand Hill - Brooksville Raid', 'link':'/mosaic/22596', 'city':' Spring Hill'});
	currentArray.append({'name':'Passion all Around', 'link':'/mosaic/23146', 'city':' DeBary'});
	currentArray.append({'name':'Lakeland conquest', 'link':'/mosaic/5429', 'city':' Lakeland'});
	currentArray.append({'name':'South Florida Weather', 'link':'/mosaic/20455', 'city':' Miami'});
	currentArray.append({'name':'Delray Beach', 'link':'/mosaic/22384', 'city':' Delray Beach'});
	currentArray.append({'name':'Make Alice Wonder', 'link':'/mosaic/25661', 'city':' Fort Myers'});
	currentArray.append({'name':'Miami  Smileday', 'link':'/mosaic/628', 'city':' Miami'});

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
