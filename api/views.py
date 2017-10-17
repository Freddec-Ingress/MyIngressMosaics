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
	
	currentArray.append('Moraga Meander');
	currentArray.append('Niles Mission Series');
	currentArray.append('Orinda Overview');
	currentArray.append('SF Peak Walk');
	currentArray.append('Show your colors');
	currentArray.append('UCDAVIS');
	currentArray.append('WeHo Los Angeles');
	currentArray.append('IRVINE');
	currentArray.append('RANCHO');
	currentArray.append('PORTAL Upland');
	currentArray.append('RESIST Rancho');
	currentArray.append('Explore Malibu');
	currentArray.append('SD Pride 2015');
	currentArray.append('Mmm Donuts');
	currentArray.append('Getting to know the City of Santee');
	currentArray.append('UCI Task Group 2');
	currentArray.append('UCI 50th Anniversary');
	currentArray.append('UCI Infinity');
	currentArray.append('UCI Task Group 3');
	currentArray.append('Knott s Camp Snoopy');
	currentArray.append('Hakone');
	currentArray.append('Historic Castro District');
	currentArray.append('Goleta Series');
	currentArray.append('Murals of Lompoc Mural Mission');
	currentArray.append('XM Obsessed');
	currentArray.append('Ballona Park');
	currentArray.append('Disney Hack-the-Lot');
	currentArray.append('CSUN Banner');
	currentArray.append('Cat Collecting in Pacoima CA');
	currentArray.append('Hitachi Tree');
	currentArray.append('Julian Walking Tour');
	currentArray.append('Pavilion Park');
	currentArray.append('90504');
	currentArray.append('Resist  Jackson');
	currentArray.append('Santana Row Mural');
	currentArray.append('SouthBay Illuminati');
	currentArray.append('Eldorado Park');
	currentArray.append('Fort Humboldt at Bucksport');
	currentArray.append('Hack Ocean Animals');
	currentArray.append('Expo Line - LA Metro');
	currentArray.append('Mystic Training');
	currentArray.append('#YOLO Around Lake Elizabeth');
	currentArray.append('FEEL THE KERN');
	currentArray.append('SFSU Tour');
	currentArray.append('Annoy the Glendale Mafia');
	currentArray.append('Circle City Allstars');
	currentArray.append('Six Flags of Discovery Kingdom');
	currentArray.append('Discover Gridley');
	currentArray.append('Naples Sunset');
	currentArray.append('Brace Yourself');
	currentArray.append('Sunnyvale Downtown');
	currentArray.append('La Cañada - Hack The Zip Code');
	currentArray.append('90503 Zip Code');
	currentArray.append('90505 Zip Code');
	currentArray.append('Rainbow Cat');
	currentArray.append('Tumbling Pandas');
	currentArray.append('Beautiful Folsom Lake College');
	currentArray.append('South Bay Portal Party');
	currentArray.append('Rohnert Park The Friendly City');
	currentArray.append('Palo Alto Resist');
	currentArray.append('MV Trees');
	currentArray.append('Rainbow cat parade in Old Fair Oaks');
	currentArray.append('Mascot Series');
	currentArray.append('From Old to New Arroyo Grande');
	currentArray.append('Smurfs Mission');
	currentArray.append('Cool Sunnyvale Rainbow');
	currentArray.append('Lodi Resist');
	currentArray.append('Foster City');
	currentArray.append('Entering Calico Ghost Town');
	currentArray.append('Chapman Operation Blue');
	currentArray.append('Chaffey Operation Blue');
	currentArray.append('Claremont Colleges Operation Blue');
	currentArray.append('Double Lima Uniform - Operation Blue');
	currentArray.append('Foxtrot Operation Blue');
	currentArray.append('Grape Day Operation Blue');
	currentArray.append('Ontario Operation Blue');
	currentArray.append('Papa Sierra - Operation Blue');
	currentArray.append('Pomona Operation Blue');
	currentArray.append('Redlands Operation Blue');
	currentArray.append('Victor Golf Operation Blue');
	currentArray.append('UCD Aggies');
	currentArray.append('Presidents of Change');
	currentArray.append('The Forgotten');
	currentArray.append('Downtown Riverbank Fun');
	currentArray.append('Escalon  California');
	currentArray.append('Isla Vista series');
	currentArray.append('Santa Clara Central Park Rainbow');
	currentArray.append('Spies of Halfmoon Bay');
	currentArray.append('IETOAD');
	currentArray.append('Downtown Culver City');
	currentArray.append('Capture UCI');
	currentArray.append('Tour Santa Monica College');
	currentArray.append('Secret Agent College');
	currentArray.append('Chaffey Quizzes');
	currentArray.append('Glyphing the College (and Gardens)');
	currentArray.append('Rainbow Bridge -  420');
	currentArray.append('Dinnertime Series');
	currentArray.append('Resist - SV');
	currentArray.append('Saratoga Noble Gases');
	currentArray.append('Plaza de Mexico');
	currentArray.append('Explore Downtown Disney');
	currentArray.append('Sculptor  architect of XM');
	currentArray.append('Coit Tower');
	currentArray.append('Magnus Reawakens  Luminescent Heart Pasadena');
	currentArray.append('Magnus Reawakens  Luminescent Heart VV');
	currentArray.append('Magnus Reawakens  Luminescent Heart  Fullerton');
	currentArray.append('Magnus Reawakens  Luminescent Heart  Irvine');
	currentArray.append('Magnus Reawakens  Luminescent Heart  Riverside');
	currentArray.append('Magnus Reawakens  Luminescent Heart  Santa Ana');
	currentArray.append('Magnus Reawakens  Luminescent Heart SB');
	currentArray.append('Get out and Walk Pandas');
	currentArray.append('Magnus Reawakens  Luminescent Heart Pasadena CalTech');
	currentArray.append('Red Pandas');
	currentArray.append('Random Pandas');
	currentArray.append('Resonessence Banner');
	currentArray.append('Mood Swing Pandas');
	currentArray.append('Resonnessence');
	currentArray.append('Magnus Reawakens Resonessence');
	currentArray.append('Carpinteria Seals');
	currentArray.append('Carpinteria Pelicans');
	currentArray.append('History San Jose   A Walk in the park');
	currentArray.append('Rainbow Pandas');
	currentArray.append('Solar Eclipse');
	currentArray.append('Yosemite Crawl - Waterfall Series');
	currentArray.append('You Otter See This');
	currentArray.append('Lily Capital Smith River CA');
	currentArray.append('Visit Crescent City California');
	currentArray.append('Skylawn');
	currentArray.append('Oceanside Parks and Land Marks');
	currentArray.append('Celtic Series - XF Ribbon - Oceanside');
	currentArray.append('Aviation History at March Field');
	currentArray.append('San Leandro Marina');
	currentArray.append('rainbow fruit');
	currentArray.append('Resist (1 of 7)');
	currentArray.append('Earn the Seven Power Coins - CA');
	currentArray.append('San Pedro mini series');
	currentArray.append('Woodland Movie in Old Town');
	currentArray.append('Oakland Zoo');
	currentArray.append('Maths');
	currentArray.append('The Animal Kingdom');
	currentArray.append('SF Cable Car Powell-Hyde');
	currentArray.append('SF Historic Streetcar #1061');
	currentArray.append('GGB San Francisco');
	currentArray.append('Lake Merritt Walk');
	currentArray.append('Love Lafayette');
	currentArray.append('Pacific Grove Mosaic');
	currentArray.append('San Francisco s Pyramid');
	currentArray.append('Tour of Downtown Brentwood');
	currentArray.append('Visit Modesto Banner');
	currentArray.append('Winter Rose Mosaic');
	currentArray.append('Chico  CA - mosaic');
	currentArray.append('Clovis');
	currentArray.append('Los Angeles Skyline');
	currentArray.append('Explore Thousand Oaks');
	currentArray.append('Bixby Bridge - Clouds (add-on)');
	currentArray.append('Menifee Tour');
	currentArray.append('I frack in your general direction');
	currentArray.append('Fresno');
	currentArray.append('DCA Disney California Adventure');
	currentArray.append('All Aboard  Next Stop Mainstreet USA  DL01');
	currentArray.append('DL Disneyland');
	currentArray.append('Belmont Park Mural');
	currentArray.append('OC Resistance');
	currentArray.append('San Mateo-Hayward Bridge');
	currentArray.append('SF Zoo Mission');
	currentArray.append('Frank Lloyd Wright');
	currentArray.append('Downtown Visalia');
	currentArray.append('Edwards AFB Exploration');
	currentArray.append('Explore the Saddleback Valley');
	currentArray.append('San Pedro Waterfront');
	currentArray.append('Explore Lakeside');
	currentArray.append('Flight Test Explorers');
	currentArray.append('Castle Air Museum B52 banner');
	currentArray.append('SF S200 LRV Introduction');
	currentArray.append('Old Town Eureka');
	currentArray.append('Third Ave   Chula Vista Mural');
	currentArray.append('Signal Hill');
	currentArray.append('Tour Old Sacramento');
	currentArray.append('sddave s excellent adventure');
	currentArray.append('Fortuna Depot Museum');
	currentArray.append('Historic Sixth Street Viaduct');
	currentArray.append('La Habra Bengal');
	currentArray.append('Divisadero tour');
	currentArray.append('Mariner s Mural');
	currentArray.append('Santa Clara University');
	currentArray.append('Los Gatos');
	currentArray.append('805 X-Faction Series');
	currentArray.append('Willow Glen Charm');
	currentArray.append('South Park Mural');
	currentArray.append('Doctors');
	currentArray.append('The San Gabriel Mission');
	currentArray.append('California Theatre');
	currentArray.append('City of Goleta series');
	currentArray.append('Explore this area Uno');
	currentArray.append('Upper Paramount Iceland');
	currentArray.append('Visit Bugs Land and Cars Land');
	currentArray.append('UCLA Bruins Pride');
	currentArray.append('Welcome to Night Vale');
	currentArray.append('Queen Mary Tour');
	currentArray.append('Assault on Hill 88');
	currentArray.append('Honor our Veterans IngressFS');
	currentArray.append('Defend the Downey Farm');
	currentArray.append('Carpinteria Beach');
	currentArray.append('Anaheim Hills Scenic Route (AugustPhoebe)');
	currentArray.append('Enlightened Strike Series 1');
	currentArray.append('Adam West Tribute');
	currentArray.append('Visit Roseville Fountains');
	currentArray.append('Coronado Bridge');
	currentArray.append('Santa Monica Starburst');
	currentArray.append('SF Muni Metro Map');
	currentArray.append('Citrus Heights Sights');
	currentArray.append('Bay Bridge');
	currentArray.append('Calle 24 - Juri Commons');
	currentArray.append('Fresno County Courthouse Park Mission');
	currentArray.append('Glory of the Verdant Cow');
	currentArray.append('Mountain View Cemetery');
	currentArray.append('Tamalpais View');
	currentArray.append('Tour Downtown Sacramento');
	currentArray.append('Alameda Tour');
	currentArray.append('Welcome to Chico State');
	currentArray.append('Riverside Founder Memorial');
	currentArray.append('Explore the area In-N-Outs');
	currentArray.append('Imperial Beach Pier');
	currentArray.append('Balboa Mosaic');
	currentArray.append('Campbell Farmer s Market');
	currentArray.append('Point Reyes Shipwreck');
	currentArray.append('Island Sunset');
	currentArray.append('San Diego Postcard');
	currentArray.append('San Diego Zoo');
	currentArray.append('Butterfly Mission');
	currentArray.append('Norh Park Mural');
	currentArray.append('Hayward  The Black Hole');
	currentArray.append('Sun Leandro');
	currentArray.append('Explore UCSB Campus');
	currentArray.append('Downtown Ventura');
	currentArray.append('Visalia courthouse');
	currentArray.append('Turquoise Butterfly');
	currentArray.append('Hanford courthouse');
	currentArray.append('Polk Street Stroll');
	currentArray.append('King of the Missions - San Luis Rey');
	currentArray.append('Path of the Enlightened');
	currentArray.append('Temple City Camellias');
	currentArray.append('HB Pier Pressure');
	currentArray.append('Hepner Hall - SDSU');
	currentArray.append('La Jolla Children s Pool');
	currentArray.append('Peninsula Power');
	currentArray.append('Redondo Beach Pier');
	currentArray.append('San Mateo County History Museum');
	currentArray.append('Discover Solvang');
	currentArray.append('Enlighten the World');
	currentArray.append('Monterey Bay Aquarium');
	currentArray.append('Paradise Banner');
	currentArray.append('The Gryffindor Trio');
	currentArray.append('Visit Adventureland and Critter Country');
	currentArray.append('Colma');
	currentArray.append('Mainstreet U S A');
	currentArray.append('Weeping Angel');
	currentArray.append('Explorer of Lakewood');
	currentArray.append('SeaWorld is the Place to Be');
	currentArray.append('Municipal Pier Redondo');
	currentArray.append('Oceanside Pier Mosaic');
	currentArray.append('Visit Tomorrowland');
	currentArray.append('Catalina Mosaic');
	currentArray.append('Ocean Beach Pier');
	currentArray.append('Seal Beach Pier Mural');
	currentArray.append('La Mirada Agricultural History');
	currentArray.append('Victorian Ferndale Walkabout');
	currentArray.append('Crystal Pier');
	currentArray.append('Sunset Cliffs');
	currentArray.append('Storming The Beachesl');
	currentArray.append('Explore UC Irvine');
	currentArray.append('Capture the NTC Command Center');
	currentArray.append('LACoFD Proud Protectors');
	currentArray.append('Outgress');
	currentArray.append('PV Resistance');
	currentArray.append('Fabulous Hillcrest');
	currentArray.append('Visit Fantasy Land');
	currentArray.append('Well Qualified to Represent the LBC');
	currentArray.append('Wienermobile');
	currentArray.append('Discover Lake Balboa Park (SFV  CA)');
	currentArray.append('San Mateo');
	currentArray.append('Night at the Drive-In');
	currentArray.append('Mission Dolores');
	currentArray.append('Tour of Oroville');
	currentArray.append('Bakersfield - All American City');
	currentArray.append('Capture the Whaley House');
	currentArray.append('Petaluma Riviera');
	currentArray.append('Octopus At Pixels');
	currentArray.append('Explore Little Tokyo [Shō-tōkyō]');
	currentArray.append('LLU Vision 2020');
	currentArray.append('SFV Ingress Ponies');
	currentArray.append('Humboldt Fog');
	currentArray.append('Downtown Chico Adventure');
	currentArray.append('Verdant Storm of Enlightenment');
	currentArray.append('Fisherman s Wharf');
	currentArray.append('Mission San Luis Obispo');
	currentArray.append('rancho banner');
	currentArray.append('5k at L B J');
	currentArray.append('San Ysidro Mural');
	currentArray.append('In Memory of Officer Galvez');
	currentArray.append('Betty s Glasses');
	currentArray.append('Explore the Coachella Valley');
	currentArray.append('San José Grand Voyage V');
	currentArray.append('Explore Palm Springs');
	currentArray.append('Morro Rock');
	currentArray.append('Historical Anaheim Packing House');
	currentArray.append('Who s got the AXE - 2');
	currentArray.append('Martinez Regional Shoreline');
	currentArray.append('May the force be with MV');
	currentArray.append('Well here we are  Pismo Beach');
	currentArray.append('Chicano Park Mural');
	currentArray.append('Fine Arts Museums of San Francisco');
	currentArray.append('Arcata historic tour series');
	currentArray.append('Get in the van BRO');
	currentArray.append('Learn by Doing');
	currentArray.append('Paramount Iceland');
	currentArray.append('Santa Cruz Starburst');
	currentArray.append('KermiWan Kenobi');
	currentArray.append('Medals Series - CA');
	currentArray.append('Jewel of the Missions');
	currentArray.append('Sunset Wild Run');
	currentArray.append('Wilshire Facts');
	currentArray.append('Sapphire Cyborg Components');
	currentArray.append('Visit Buena Vista St and Hollywood Land');
	currentArray.append('Newport Pier in all its Bluety');
	currentArray.append('Tall Ships of Dana Point');
	currentArray.append('Black Cat');
	currentArray.append('Visit Downtown disney');
	currentArray.append('Visit Paradise Pier');
	currentArray.append('Haybalers Of Hollister');
	currentArray.append('There s Something About');
	currentArray.append('Plaza Mexico');
	currentArray.append('Memorial To Ghost Ship');
	currentArray.append('Bueller    Bueller    Bueller');
	currentArray.append('NOHO Circus Liquor');
	currentArray.append('Taquero Mucho');
	currentArray.append('Mothers Day - SD 2017');
	currentArray.append('Magnus Reawakens  Luminescent Heart Park B');
	currentArray.append('Magnus Reawakens  Luminescent Heart Pasadena  CA');
	currentArray.append('Magnus Reawakens  Luminescent Heart LA #2');
	currentArray.append('One if by land  and two if by sea');
	currentArray.append('Stearns Wharf');
	currentArray.append('Ferry Building');
	currentArray.append('Alamo Square Painted Ladies');
	currentArray.append('Saint Raphael the Archangel');
	currentArray.append('The Milpitas Monster');
	currentArray.append('UCSC Campus Tour');
	currentArray.append('Ghost Heart');
	currentArray.append('Sideways Mission Series');
	currentArray.append('Who s got the AXE');
	currentArray.append('Irvine  The Final Frontier');
	currentArray.append('Resistance is not Futile in Irvine');
	currentArray.append('Unity Through Enlightenment');
	currentArray.append('Solar Eclipse-Red');
	currentArray.append('Memorial Day – SD 2017');
	currentArray.append('Merced Theatre at Night');
	currentArray.append('Hamilton Air Force Base');
	currentArray.append('The Walter Pyramid');
	currentArray.append('Solar Eclipse-Water');
	currentArray.append('Fillmore Jazz Sessions');
	currentArray.append('Dance your way around Old Town');
	currentArray.append('4th of July');
	currentArray.append('Father’s Day – SD2017');
	currentArray.append('Pier Cafe');
	currentArray.append('Porter Squiggle');
	currentArray.append('See the Sea Turtles');
	currentArray.append('SD Comic-Con');
	currentArray.append('Camp Pendleton Mosaic');
	currentArray.append('Encinitas Sunset');
	currentArray.append('Fallbrook The Avocado Capital');
	currentArray.append('HB Solar Eclipse');
	currentArray.append('Darkside');
	currentArray.append('Zen Frog');
	currentArray.append('Colton Hall');
	currentArray.append('MissionDay Oakland');
	currentArray.append('Santa Cruz Art Tour Series');
	currentArray.append('Explore Galt Ca');
	currentArray.append('Bointa Reistance Key');
	currentArray.append('SMC Moraga');
	currentArray.append('Barbary Coast Trail');
	currentArray.append('DTLA - Full Tour');
	currentArray.append('Explore Your World');
	currentArray.append('Island Life');
	currentArray.append('John Drake Sloat');
	currentArray.append('Livermore the Odyssey');
	currentArray.append('OAKLAND HISTORY');
	currentArray.append('Protect the nothing');
	currentArray.append('UC Berkeley Campus');
	currentArray.append('Visit Elk Grove CA');
	currentArray.append('Liberty Day  1901');
	currentArray.append('Santa Barbara');
	currentArray.append('Santa Monica Series');
	currentArray.append('Geisel Library');
	currentArray.append('Fullerton Arboretum');
	currentArray.append('UCI Task Group 1');
	currentArray.append('AVI Lancaster');
	currentArray.append('Journey to The Historic Palace of Fine Arts');
	currentArray.append('Historic North Beach');
	currentArray.append('Neon Nights');
	currentArray.append('AVII');
	currentArray.append('Motherboard SOMA');
	currentArray.append('Long Beach Enlightened');
	currentArray.append('Monarch Butterfly');
	currentArray.append('The Birds Movie Homage');
	currentArray.append('Shark Quest');
	currentArray.append('Machine Banner');
	currentArray.append('San José Grand Voyage II');
	currentArray.append('San José Grand Voyage III');
	currentArray.append('San José Grand Voyage IV');
	currentArray.append('Shark Attack');
	currentArray.append('San Clemente Pier at Sunset');
	currentArray.append('Operation Pomegranate');
	currentArray.append('Route 66');
	currentArray.append('Roman Mars Would Approve');
	currentArray.append('American Bald Eagle');
	currentArray.append('Fun Times at the Balboa Fun Zone');
	currentArray.append('Palo Alto Zodiac');
	currentArray.append('Game On');
	currentArray.append('Magnus Reawakens  Luminescent Heart LA Edition');
	currentArray.append('Explore Yucaipa');
	currentArray.append('Story of the Scorpion and the Frog');
	currentArray.append('Cali RES Flag');
	currentArray.append('Questionable Arrow-Dynamics in SF');
	currentArray.append('MD  Irvine');
	currentArray.append('El Campanil Theatre at Night');
	currentArray.append('The Huntington');
	currentArray.append('Carquinez Mural');
	currentArray.append('Eureka Ca Mission Series');
	currentArray.append('The Bixby Bridge');
	currentArray.append('Yin-Yang');
	currentArray.append('Hawthorne Hornets');
	currentArray.append('Walking the Walk of Fame');
	currentArray.append('66 Tour');
	currentArray.append('Journey to The historic Cliff House');
	currentArray.append('Old Town Camarillo');
	currentArray.append('Anonymously Through Lynwood - America');
	currentArray.append('Ventura Pier');
	currentArray.append('MissionDay San Diego');
	currentArray.append('San José Grand Voyage I');
	currentArray.append('Mission Santa Barbara');
	currentArray.append('Team Tricksters');
	currentArray.append('Aim to misbehave  in San Mateo');
	currentArray.append('Panda Play Time');
	currentArray.append('Ghost of War');
	currentArray.append('SF Muni at 100 #1');
	currentArray.append('Fiat Lux');
	currentArray.append('Folsom Banner');
	currentArray.append('Temecula Monopoly');
	currentArray.append('Balboa Park s 100th Celebration');
	currentArray.append('The Downey D-Bags');
	currentArray.append('Great Park');
	currentArray.append('Summer of Love');
	currentArray.append('Explore North Lake Tahoe');
	currentArray.append('Help me Obi Wan');
	currentArray.append('Light and Shadows');
	currentArray.append('V  is for Vendetta');
	currentArray.append('Resist this MTZ');
	currentArray.append('Lost Boys of Santa Cruz');
	currentArray.append('City of Burbank');
	currentArray.append('Party Time on 2nd Street');
	currentArray.append('Actransit Bus Dash');
	currentArray.append('Sacramento Skyline');
	currentArray.append('San Jose Ingress United');
	currentArray.append('Hack your way to San Diego Enlightment');
	currentArray.append('American Presidents');
	currentArray.append('THE KEY');
	currentArray.append('Laguna Beach Lifeguard');
	currentArray.append('1913 Corona Road Race');
	currentArray.append('PAC Theater Mural');
	currentArray.append('Jedi Smurf');
	currentArray.append('South County FBT');
	currentArray.append('UCR Highlanders Mosaic');
	currentArray.append('The Lone Ranger');
	currentArray.append('Glendale Series');
	currentArray.append('Surfs up WC');
	currentArray.append('Rancho Obi-Wan');
	currentArray.append('San Gabriel Valley');
	currentArray.append('Sacramento Enlightened');
	currentArray.append('Explore DTLA (Union Station)');
	currentArray.append('Sacramento Resistance');
	currentArray.append('Boyle Heights Examiner');
	currentArray.append('COBRA Alpha');
	currentArray.append('Pasadena');
	currentArray.append('OC Odyssey');
	currentArray.append('Golden Gate at Night');

	for item in currentArray:
		
		results = Mosaic.objects.filter(title=item)
		if results.count() < 1:
			
			obj = {
				'name': item,
			}
			
			data.append(obj)
	
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
