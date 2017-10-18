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
	
	currentArray.append({'name':'Red Faction', 'link':'/mosaic/629', 'city':'Houston'});
	currentArray.append({'name':'Faction Pride', 'link':'/mosaic/1658', 'city':'Midland'});
	currentArray.append({'name':'The Strand Street District', 'link':'/mosaic/1904', 'city':'Galveston'});
	currentArray.append({'name':'Austin Skyline', 'link':'/mosaic/3242', 'city':'Austin'});
	currentArray.append({'name':'CORPUS CHRISTI', 'link':'/mosaic/4137', 'city':'Corpus Christi'});
	currentArray.append({'name':'Main Street Chappell Hill (CHHS Tour)', 'link':'/mosaic/4977', 'city':'Chappell Hill'});
	currentArray.append({'name':'Houston Skyline', 'link':'/mosaic/4995', 'city':'Houston'});
	currentArray.append({'name':'Keep Calm and Lady Bug On', 'link':'/mosaic/6269', 'city':'Rosenberg'});
	currentArray.append({'name':'Hardin-Simmons University', 'link':'/mosaic/6626', 'city':'Abilene'});
	currentArray.append({'name':'We Love Houston', 'link':'/mosaic/8524', 'city':'Houston'});
	currentArray.append({'name':'Galveston Pleasure', 'link':'/mosaic/9115', 'city':'Galveston'});
	currentArray.append({'name':'A Hamster s Life C', 'link':'/mosaic/9227', 'city':'Sugar Land'});
	currentArray.append({'name':'Nacogdoches', 'link':'/mosaic/9335', 'city':'Nacogdoches'});
	currentArray.append({'name':'Liberty TX', 'link':'/mosaic/9656', 'city':'Liberty'});
	currentArray.append({'name':'Oyster Creek Park', 'link':'/mosaic/9663', 'city':'Sugar Land'});
	currentArray.append({'name':'Come and Take It', 'link':'/mosaic/10743', 'city':'Cypress'});
	currentArray.append({'name':'The Turtle Moves', 'link':'/mosaic/11290', 'city':'Houston'});
	currentArray.append({'name':'WAXAHACHIE  HARD TO RESIST', 'link':'/mosaic/12177', 'city':'Waxahachie'});
	currentArray.append({'name':'COMANCHE TX SCENERY', 'link':'/mosaic/12474', 'city':'Comanche'});
	currentArray.append({'name':'Frisco Commons', 'link':'/mosaic/13863', 'city':'Frisco'});
	currentArray.append({'name':'Feet on the ground', 'link':'/mosaic/14164', 'city':'Houston'});
	currentArray.append({'name':'Exploring Haltom City', 'link':'/mosaic/14447', 'city':'Haltom City'});
	currentArray.append({'name':'Who is Enlightened', 'link':'/mosaic/16257', 'city':'Tomball'});
	currentArray.append({'name':'The Republic of Texas', 'link':'/mosaic/16669', 'city':'San Antonio'});
	currentArray.append({'name':'Odessa Churches', 'link':'/mosaic/16670', 'city':'Odessa'});
	currentArray.append({'name':'Austin College - Sextet Intelligence', 'link':'/mosaic/17694', 'city':'Sherman'});
	currentArray.append({'name':'Rio DJ mission in Texas', 'link':'/mosaic/17866', 'city':'Corpus Christi'});
	currentArray.append({'name':'Ennis cat cute', 'link':'/mosaic/18241', 'city':'Ennis'});
	currentArray.append({'name':'Guitar In Flames', 'link':'/mosaic/18395', 'city':'Alvin'});
	currentArray.append({'name':'Beatles In Houston', 'link':'/mosaic/18398', 'city':'Houston'});
	currentArray.append({'name':'Restland Richardson', 'link':'/mosaic/18738', 'city':'Dallas'});
	currentArray.append({'name':'Rainbow Crest', 'link':'/mosaic/19065', 'city':'Montgomery'});
	currentArray.append({'name':'Southwestern University', 'link':'/mosaic/19429', 'city':'Georgetown'});
	currentArray.append({'name':'Crystal Skull', 'link':'/mosaic/19971', 'city':'Houston'});
	currentArray.append({'name':'The King Wears Cowboy Hat', 'link':'/mosaic/20154', 'city':'Galveston'});
	currentArray.append({'name':'All the Bacon', 'link':'/mosaic/20449', 'city':'Houston'});
	currentArray.append({'name':'Mission Day SATX USA 25 March 2017', 'link':'/mosaic/20548', 'city':'San Antonio'});
	currentArray.append({'name':'Mission from God - Pearland', 'link':'/mosaic/21013', 'city':'Pearland'});
	currentArray.append({'name':'Animal House', 'link':'/mosaic/22279', 'city':'Houston'});
	currentArray.append({'name':'Parrots of Oliveira Park 11 of 12', 'link':'/mosaic/22714', 'city':'Brownsville'});
	currentArray.append({'name':'Boya de Iquique', 'link':'/mosaic/23362', 'city':'New York'});
	currentArray.append({'name':'Conhecendo o Recanto das Emas - DF', 'link':'/mosaic/23367', 'city':'New York'});
	currentArray.append({'name':'Fortaleza de São José de Macapá', 'link':'/mosaic/23373', 'city':'New York'});
	currentArray.append({'name':'GeLA to Crosse', 'link':'/mosaic/23374', 'city':'New York'});
	currentArray.append({'name':'La Ciudad del Color', 'link':'/mosaic/23379', 'city':'New York'});
	currentArray.append({'name':'くらまえぶるっくりん', 'link':'/mosaic/23634', 'city':'New York'});
	currentArray.append({'name':'Summer on the Water', 'link':'/mosaic/23785', 'city':'Fort Worth'});
	currentArray.append({'name':'The Creed', 'link':'/mosaic/23794', 'city':'Navasota'});
	currentArray.append({'name':'Marvelous Storm', 'link':'/mosaic/24495', 'city':'Hitchcock'});
	currentArray.append({'name':'Choose Your Side', 'link':'/mosaic/24534', 'city':'Odessa'});
	currentArray.append({'name':'Forney s Blue Viper', 'link':'/mosaic/24663', 'city':'Forney'});
	currentArray.append({'name':'Marvelous Marble Falls  TX', 'link':'/mosaic/25955', 'city':'Marble Falls'});
	currentArray.append({'name':'Who s  screwdriver', 'link':'/mosaic/25998', 'city':'Fort Stockton'});
	currentArray.append({'name':'The Weapon of Choice', 'link':'/mosaic/25999', 'city':'Odessa'});
	currentArray.append({'name':'Defenders of Smurfa', 'link':'/mosaic/26102', 'city':'Frisco'});
	currentArray.append({'name':'Welcome to Round Rock  TX', 'link':'/mosaic/26710', 'city':'Round Rock'});
	currentArray.append({'name':'Monahans', 'link':'/mosaic/27411', 'city':'Monahans'});
	currentArray.append({'name':'Houston EXO5', 'link':'/mosaic/27845', 'city':'Houston'});
	currentArray.append({'name':'Barcode Banner', 'link':'/mosaic/544', 'city':'McAllen'});
	currentArray.append({'name':'The Unicorn Banner', 'link':'/mosaic/633', 'city':'Bryan'});
	currentArray.append({'name':'Are You Enlightened McKinney', 'link':'/mosaic/2142', 'city':'McKinney'});
	currentArray.append({'name':'Mustang Madness', 'link':'/mosaic/2386', 'city':'Dallas'});
	currentArray.append({'name':'Tour of the Hill Country', 'link':'/mosaic/3248', 'city':'Georgetown'});
	currentArray.append({'name':'Allen Eagles', 'link':'/mosaic/3264', 'city':'Allen'});
	currentArray.append({'name':'Come explore  Fort Worth Stockyards', 'link':'/mosaic/3333', 'city':'Fort Worth'});
	currentArray.append({'name':'Go  Miners', 'link':'/mosaic/4264', 'city':'El Paso'});
	currentArray.append({'name':'Horned Frogs', 'link':'/mosaic/5182', 'city':'Fort Worth'});
	currentArray.append({'name':'Corpus Christi Harbor Bridge', 'link':'/mosaic/5936', 'city':'Corpus Christi'});
	currentArray.append({'name':'Houston is Inspired', 'link':'/mosaic/6227', 'city':'Houston'});
	currentArray.append({'name':'As You Wish', 'link':'/mosaic/7088', 'city':'College Station'});
	currentArray.append({'name':'Colorful Flowers', 'link':'/mosaic/7935', 'city':'Houston'});
	currentArray.append({'name':'Beaumont Skyline', 'link':'/mosaic/8799', 'city':'Beaumont'});
	currentArray.append({'name':'Greetings from Houston', 'link':'/mosaic/9152', 'city':'Houston'});
	currentArray.append({'name':'A Hamster s Life B', 'link':'/mosaic/9575', 'city':'Houston'});
	currentArray.append({'name':'Oaks of League City', 'link':'/mosaic/9606', 'city':'League City'});
	currentArray.append({'name':'UTRGV Edinburg Campus Stroll', 'link':'/mosaic/9629', 'city':'Edinburg'});
	currentArray.append({'name':'Misty Mood', 'link':'/mosaic/9838', 'city':'Houston'});
	currentArray.append({'name':'Interstate MUD district exploration', 'link':'/mosaic/9909', 'city':'Katy'});
	currentArray.append({'name':'Imperial Sugar Factory', 'link':'/mosaic/10033', 'city':'Sugar Land'});
	currentArray.append({'name':'Synchronicity of Color - Blue', 'link':'/mosaic/10086', 'city':'Houston'});
	currentArray.append({'name':'Synchronicity of Color - Red', 'link':'/mosaic/10087', 'city':'Houston'});
	currentArray.append({'name':'Gotta Catch em  All', 'link':'/mosaic/10740', 'city':'Kerrville'});
	currentArray.append({'name':'Cypress Moon', 'link':'/mosaic/10744', 'city':'Cypress'});
	currentArray.append({'name':'JBT Houston', 'link':'/mosaic/10745', 'city':'Houston'});
	currentArray.append({'name':'Moo-Lah Banner', 'link':'/mosaic/10921', 'city':'Stephenville'});
	currentArray.append({'name':'Granbury Courthouse Banner', 'link':'/mosaic/10922', 'city':'Granbury'});
	currentArray.append({'name':'Ol Doc s Soda Shop Banner', 'link':'/mosaic/10923', 'city':'Dublin'});
	currentArray.append({'name':'GLEN ROSE BANNER', 'link':'/mosaic/10924', 'city':'Glen Rose'});
	currentArray.append({'name':'City of Mansfield', 'link':'/mosaic/11321', 'city':'Mansfield'});
	currentArray.append({'name':'Discover Port Aransas', 'link':'/mosaic/11325', 'city':'Aransas Pass'});
	currentArray.append({'name':'The Grace Museum', 'link':'/mosaic/11358', 'city':'Abilene'});
	currentArray.append({'name':'Texas Trekker', 'link':'/mosaic/11553', 'city':'Wharton'});
	currentArray.append({'name':'Mermaid Units', 'link':'/mosaic/11721', 'city':'Galveston'});
	currentArray.append({'name':'Texas Interstate Tour', 'link':'/mosaic/11860', 'city':'Merkel'});
	currentArray.append({'name':'A Day to Remember Geogetown', 'link':'/mosaic/12185', 'city':'Georgetown'});
	currentArray.append({'name':'Birthplace of a Flag', 'link':'/mosaic/12191', 'city':'Conroe'});
	currentArray.append({'name':'BROWNWOOD MOSAIC', 'link':'/mosaic/12195', 'city':'Early'});
	currentArray.append({'name':'Dallas Arboretum', 'link':'/mosaic/12199', 'city':'Dallas'});
	currentArray.append({'name':'EASTLAND COLOR SPLASH', 'link':'/mosaic/12203', 'city':'Eastland'});
	currentArray.append({'name':'The Falls Historical Mural', 'link':'/mosaic/12489', 'city':'Wichita Falls'});
	currentArray.append({'name':'MINERAL WELLS TOUR', 'link':'/mosaic/12513', 'city':'Mineral Wells'});
	currentArray.append({'name':'Texas State', 'link':'/mosaic/12687', 'city':'San Marcos'});
	currentArray.append({'name':'Space for Everyone', 'link':'/mosaic/12833', 'city':'Houston'});
	currentArray.append({'name':'Proud American Banner', 'link':'/mosaic/12986', 'city':'Fort Worth'});
	currentArray.append({'name':'Catch Pikachu', 'link':'/mosaic/12991', 'city':'Houston'});
	currentArray.append({'name':'Psychedelic Woman', 'link':'/mosaic/13004', 'city':'Houston'});
	currentArray.append({'name':'Space City', 'link':'/mosaic/13067', 'city':'League City'});
	currentArray.append({'name':'Congress Ave Bat Bridge', 'link':'/mosaic/13189', 'city':'Austin'});
	currentArray.append({'name':'Fireworks', 'link':'/mosaic/13246', 'city':'Houston'});
	currentArray.append({'name':'Essence', 'link':'/mosaic/13290', 'city':'Houston'});
	currentArray.append({'name':'Austin  Live Music Capital of the World', 'link':'/mosaic/13355', 'city':'Austin'});
	currentArray.append({'name':'SA Riverwalk', 'link':'/mosaic/13492', 'city':'San Antonio'});
	currentArray.append({'name':'Neon Rain', 'link':'/mosaic/14343', 'city':'Navasota'});
	currentArray.append({'name':'Explore Fort Bend County', 'link':'/mosaic/14419', 'city':'Needville'});
	currentArray.append({'name':'Sweet Dreams', 'link':'/mosaic/14474', 'city':'Houston'});
	currentArray.append({'name':'Justice Will Prevail', 'link':'/mosaic/14478', 'city':'Bryan'});
	currentArray.append({'name':'Light vs Dark', 'link':'/mosaic/14722', 'city':'Bryan'});
	currentArray.append({'name':'A stroll through the Yachting Capital of Texas', 'link':'/mosaic/15154', 'city':'Kemah'});
	currentArray.append({'name':'The Torch of Friendship', 'link':'/mosaic/15697', 'city':'San Antonio'});
	currentArray.append({'name':'Loyal Trooper', 'link':'/mosaic/16096', 'city':'Houston'});
	currentArray.append({'name':'All About Old Town Spring', 'link':'/mosaic/16360', 'city':'Spring'});
	currentArray.append({'name':'University of Houston Banner', 'link':'/mosaic/16428', 'city':'Houston'});
	currentArray.append({'name':'The Way of the Hero', 'link':'/mosaic/16432', 'city':'Conroe'});
	currentArray.append({'name':'Touring San Marcos', 'link':'/mosaic/16671', 'city':'San Marcos'});
	currentArray.append({'name':'Fair Park Ferris Wheel', 'link':'/mosaic/17087', 'city':'Dallas'});
	currentArray.append({'name':'Stunning Sunset', 'link':'/mosaic/17248', 'city':'Houston'});
	currentArray.append({'name':'Bluebonnets', 'link':'/mosaic/17249', 'city':'Houston'});
	currentArray.append({'name':'Día de Muertos', 'link':'/mosaic/17270', 'city':'Houston'});
	currentArray.append({'name':'ROTT banner', 'link':'/mosaic/17693', 'city':'Fort Worth'});
	currentArray.append({'name':'Sea Breeze and Sunshine', 'link':'/mosaic/17709', 'city':'Corpus Christi'});
	currentArray.append({'name':'Richmond Bridge', 'link':'/mosaic/17755', 'city':'Richmond'});
	currentArray.append({'name':'Scottland in Texas  mission', 'link':'/mosaic/17867', 'city':'Corpus Christi'});
	currentArray.append({'name':'Burkeville', 'link':'/mosaic/17871', 'city':'Burkeville'});
	currentArray.append({'name':'Splatter', 'link':'/mosaic/17951', 'city':'Midland'});
	currentArray.append({'name':'Nacho Thang', 'link':'/mosaic/18555', 'city':'Seabrook'});
	currentArray.append({'name':'On Moonlight Bay', 'link':'/mosaic/18736', 'city':'Kemah'});
	currentArray.append({'name':'Conquer Walter Hall', 'link':'/mosaic/18942', 'city':'League City'});
	currentArray.append({'name':'Fredericksburg Banner', 'link':'/mosaic/19245', 'city':'Fredericksburg'});
	currentArray.append({'name':'The Johnson Treatment', 'link':'/mosaic/19273', 'city':'Johnson City'});
	currentArray.append({'name':'Wildflower Center - Austin', 'link':'/mosaic/19278', 'city':'Austin'});
	currentArray.append({'name':'Zilker Gardens Banner', 'link':'/mosaic/19282', 'city':'Austin'});
	currentArray.append({'name':'Light', 'link':'/mosaic/19620', 'city':'Tomball'});
	currentArray.append({'name':'Austin Capitol Complex Stroll', 'link':'/mosaic/19621', 'city':'Austin'});
	currentArray.append({'name':'Neon Sky', 'link':'/mosaic/19675', 'city':'Conroe'});
	currentArray.append({'name':'Rainbow BD', 'link':'/mosaic/19681', 'city':'Henderson'});
	currentArray.append({'name':'Tour of New Braunfels', 'link':'/mosaic/19682', 'city':'New Braunfels'});
	currentArray.append({'name':'Wonderland - Georgetown', 'link':'/mosaic/19721', 'city':'Georgetown'});
	currentArray.append({'name':'Beautiful Ballerina', 'link':'/mosaic/19742', 'city':'Houston'});
	currentArray.append({'name':'Rowlett Tornado', 'link':'/mosaic/19918', 'city':'Rowlett'});
	currentArray.append({'name':'Elf Girl of Palestine', 'link':'/mosaic/19929', 'city':'Palestine TX'});
	currentArray.append({'name':'Ranch Wrangler', 'link':'/mosaic/20374', 'city':'Houston'});
	currentArray.append({'name':'Gon to Pearland', 'link':'/mosaic/20415', 'city':'Pearland'});
	currentArray.append({'name':'Peacocks Gone Wild', 'link':'/mosaic/20446', 'city':'Galveston'});
	currentArray.append({'name':'Blueprints', 'link':'/mosaic/20865', 'city':'Addison'});
	currentArray.append({'name':'Storm Over Alvin  TX', 'link':'/mosaic/21012', 'city':'Alvin'});
	currentArray.append({'name':'Watch McKinney Grow', 'link':'/mosaic/21053', 'city':'McKinney'});
	currentArray.append({'name':'Animal Magnetism', 'link':'/mosaic/21277', 'city':'Houston'});
	currentArray.append({'name':'Animal Nature', 'link':'/mosaic/21278', 'city':'Houston'});
	currentArray.append({'name':'金門後浦小鎮', 'link':'/mosaic/21447', 'city':'New York'});
	currentArray.append({'name':'Dragon s Breath', 'link':'/mosaic/21709', 'city':'Beaumont'});
	currentArray.append({'name':'Lady Phoenix', 'link':'/mosaic/22295', 'city':'Beaumont'});
	currentArray.append({'name':'Link All the Kitties', 'link':'/mosaic/22697', 'city':'Houston'});
	currentArray.append({'name':'Corgi Amp', 'link':'/mosaic/22967', 'city':'Houston'});
	currentArray.append({'name':'Guardians of Light', 'link':'/mosaic/23162', 'city':'Houston'});
	currentArray.append({'name':'ACC Dolphins', 'link':'/mosaic/23386', 'city':'Alvin'});
	currentArray.append({'name':'Alchemy', 'link':'/mosaic/23387', 'city':'Houston'});
	currentArray.append({'name':'Bastrop Fire', 'link':'/mosaic/23431', 'city':'Bastrop'});
	currentArray.append({'name':'Congress Avenue - 1913', 'link':'/mosaic/23441', 'city':'Austin'});
	currentArray.append({'name':'Huttopotamus', 'link':'/mosaic/23451', 'city':'Hutto'});
	currentArray.append({'name':'Zero F cks Given', 'link':'/mosaic/23630', 'city':'Anderson'});
	currentArray.append({'name':'open your eyes', 'link':'/mosaic/23868', 'city':'Spring'});
	currentArray.append({'name':'Requiem', 'link':'/mosaic/23952', 'city':'Houston'});
	currentArray.append({'name':'Time Keeper', 'link':'/mosaic/23955', 'city':'San Antonio'});
	currentArray.append({'name':'Fireside Romance', 'link':'/mosaic/23979', 'city':'Spring'});
	currentArray.append({'name':'Love - Houston', 'link':'/mosaic/24094', 'city':'Houston'});
	currentArray.append({'name':'Odessa is Cool', 'link':'/mosaic/24178', 'city':'Odessa'});
	currentArray.append({'name':'MD  Arlington', 'link':'/mosaic/24179', 'city':'Arlington'});
	currentArray.append({'name':'City Limits', 'link':'/mosaic/24183', 'city':'Odessa'});
	currentArray.append({'name':'Welcome to Tyler', 'link':'/mosaic/24376', 'city':'Tyler TX'});
	currentArray.append({'name':'South Congress Mosey', 'link':'/mosaic/24379', 'city':'Austin'});
	currentArray.append({'name':'Crew love', 'link':'/mosaic/24678', 'city':'Houston'});
	currentArray.append({'name':'City of Houston', 'link':'/mosaic/24996', 'city':'Houston'});
	currentArray.append({'name':'Fight the portal network', 'link':'/mosaic/25398', 'city':'Mesquite'});
	currentArray.append({'name':'I Like Missions', 'link':'/mosaic/25551', 'city':'Houston'});
	currentArray.append({'name':'Red Bird Rising', 'link':'/mosaic/25586', 'city':'Victoria'});
	currentArray.append({'name':'STEPHENVILLE DAY TRIPPIN', 'link':'/mosaic/25592', 'city':'Stephenville'});
	currentArray.append({'name':'STOCKYARDS SURPRISE', 'link':'/mosaic/25594', 'city':'Fort Worth'});
	currentArray.append({'name':'Cherry Blossoms', 'link':'/mosaic/25824', 'city':'Sugar Land'});
	currentArray.append({'name':'Passing through Lampasas', 'link':'/mosaic/25923', 'city':'Lampasas'});
	currentArray.append({'name':'Stop  Copper time', 'link':'/mosaic/26209', 'city':'Flower Mound'});
	currentArray.append({'name':'Rainbow Nuzzles', 'link':'/mosaic/26215', 'city':'Pearland'});
	currentArray.append({'name':'TX Blue Dragon', 'link':'/mosaic/26471', 'city':'San Antonio'});
	currentArray.append({'name':'Fireflies', 'link':'/mosaic/26490', 'city':'Sugar Land'});
	currentArray.append({'name':'Cat s Meow', 'link':'/mosaic/26584', 'city':'Richmond'});
	currentArray.append({'name':'Be Someone', 'link':'/mosaic/26792', 'city':'Houston'});
	currentArray.append({'name':'Central East Austin', 'link':'/mosaic/27275', 'city':'Austin'});
	currentArray.append({'name':'Rice University', 'link':'/mosaic/27320', 'city':'Houston'});
	currentArray.append({'name':'Here be dragons', 'link':'/mosaic/27429', 'city':'Round Rock'});
	currentArray.append({'name':'Prowling Round Rock', 'link':'/mosaic/27435', 'city':'Round Rock'});
	currentArray.append({'name':'We Have Achieved Ingress', 'link':'/mosaic/27446', 'city':'Odessa'});
	currentArray.append({'name':'Rockin Houston  01   18', 'link':'/mosaic/27738', 'city':'Houston'});
	currentArray.append({'name':'Strike Back', 'link':'/mosaic/27940', 'city':'Odessa'});
	currentArray.append({'name':'Hack em Horns', 'link':'/mosaic/3243', 'city':'Austin'});
	currentArray.append({'name':'Veteran s Park Banner', 'link':'/mosaic/3257', 'city':'College Station'});
	currentArray.append({'name':'XFaction', 'link':'/mosaic/3266', 'city':'Denton'});
	currentArray.append({'name':'The Purge', 'link':'/mosaic/3935', 'city':'Corpus Christi'});
	currentArray.append({'name':'Houston Greener Loop', 'link':'/mosaic/4974', 'city':'Houston'});
	currentArray.append({'name':'Texas Tech Trek', 'link':'/mosaic/6625', 'city':'Lubbock'});
	currentArray.append({'name':'Welcome to Lufkin', 'link':'/mosaic/8512', 'city':'Lufkin'});
	currentArray.append({'name':'Psychedelic Dragon', 'link':'/mosaic/10944', 'city':'Houston'});
	currentArray.append({'name':'Paris in Texas', 'link':'/mosaic/11858', 'city':'Corpus Christi'});
	currentArray.append({'name':'Discovery Green', 'link':'/mosaic/12619', 'city':'Houston'});
	currentArray.append({'name':'South Padre Island', 'link':'/mosaic/13409', 'city':'South Padre Island'});
	currentArray.append({'name':'Texas Banner', 'link':'/mosaic/14103', 'city':'Georgetown'});
	currentArray.append({'name':'DOTD Mermaid', 'link':'/mosaic/15787', 'city':'Houston'});
	currentArray.append({'name':'Bike Car Brain Hustle Mission', 'link':'/mosaic/17307', 'city':'Corpus Christi'});
	currentArray.append({'name':'A Moment in Time', 'link':'/mosaic/19286', 'city':'Houston'});
	currentArray.append({'name':'Cookies and more cookies', 'link':'/mosaic/19622', 'city':'Houston'});
	currentArray.append({'name':'Animal Instinct', 'link':'/mosaic/21276', 'city':'Houston'});
	currentArray.append({'name':'Animal Kingdom', 'link':'/mosaic/21352', 'city':'Houston'});
	currentArray.append({'name':'Final Beauty', 'link':'/mosaic/21715', 'city':'Lavon'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart (Houston)', 'link':'/mosaic/22290', 'city':'Houston'});
	currentArray.append({'name':'Chainsaw', 'link':'/mosaic/22923', 'city':'Montgomery'});
	currentArray.append({'name':'Welcome to Navasota', 'link':'/mosaic/23057', 'city':'Navasota'});
	currentArray.append({'name':'Rainbow #2', 'link':'/mosaic/23732', 'city':'Houston'});
	currentArray.append({'name':'Meanwhile    at the HQ', 'link':'/mosaic/23776', 'city':'La Porte'});
	currentArray.append({'name':'Dream', 'link':'/mosaic/23996', 'city':'Houston'});
	currentArray.append({'name':'It s Just Two Brothers', 'link':'/mosaic/24960', 'city':'Spring'});
	currentArray.append({'name':'Finding Georgetown', 'link':'/mosaic/25626', 'city':'Georgetown'});
	currentArray.append({'name':'Thanks for all the fish banner', 'link':'/mosaic/25640', 'city':'Corpus Christi'});
	currentArray.append({'name':'Peace Among Worlds', 'link':'/mosaic/25668', 'city':'Houston'});
	currentArray.append({'name':'Marvelous Creations', 'link':'/mosaic/25898', 'city':'Friendswood'});
	currentArray.append({'name':'Deep in the  art of TX', 'link':'/mosaic/26667', 'city':'Granbury'});
	currentArray.append({'name':'Reflecting on Houston', 'link':'/mosaic/26907', 'city':'Houston'});
	currentArray.append({'name':'Houston Strong', 'link':'/mosaic/27453', 'city':'Houston'});
	currentArray.append({'name':'Jester Kings', 'link':'/mosaic/20157', 'city':'Austin'});
	currentArray.append({'name':'City of Dallas', 'link':'/mosaic/2313', 'city':'Dallas'});
	currentArray.append({'name':'Journey to the Pennybacker', 'link':'/mosaic/3245', 'city':'Austin'});
	currentArray.append({'name':'New York in Texas', 'link':'/mosaic/13337', 'city':'Corpus Christi'});
	currentArray.append({'name':'Texas Cowboy', 'link':'/mosaic/13338', 'city':'Corpus Christi'});
	currentArray.append({'name':'AD ASTRA', 'link':'/mosaic/18639', 'city':'Houston'});
	currentArray.append({'name':'Take an Imperial Tour of Johnson County', 'link':'/mosaic/19486', 'city':'Burleson'});
	currentArray.append({'name':'Animal Crackers - Houston Zoo - Mosaik 5 of 5', 'link':'/mosaic/21272', 'city':'Houston'});
	currentArray.append({'name':'True Colors', 'link':'/mosaic/22464', 'city':'Houston'});
	currentArray.append({'name':'altitude', 'link':'/mosaic/23845', 'city':'Spring'});
	currentArray.append({'name':'Rainbow Rose', 'link':'/mosaic/25207', 'city':'Spring'});
	currentArray.append({'name':'Jarvis', 'link':'/mosaic/26860', 'city':'Houston'});
	currentArray.append({'name':'Green All the Way', 'link':'/mosaic/4668', 'city':'Grand Prairie'});
	currentArray.append({'name':'Cruise for Classic Cars', 'link':'/mosaic/6449', 'city':'Beaumont'});
	currentArray.append({'name':'Persy Mission', 'link':'/mosaic/9490', 'city':'Fort Worth'});
	currentArray.append({'name':'Garland  Texas', 'link':'/mosaic/9947', 'city':'Dallas'});
	currentArray.append({'name':'Explore Pflugerville', 'link':'/mosaic/10741', 'city':'Pflugerville'});
	currentArray.append({'name':'Smurf the Earth San Antonio 2017', 'link':'/mosaic/24040', 'city':'San Antonio'});
	currentArray.append({'name':'Wanna Play', 'link':'/mosaic/24527', 'city':'Spring'});
	currentArray.append({'name':'Calvin Ball', 'link':'/mosaic/26463', 'city':'San Antonio'});
	currentArray.append({'name':'There s a Light - In Darkness', 'link':'/mosaic/27936', 'city':'Plano'});
	currentArray.append({'name':'A and M Banner', 'link':'/mosaic/3250', 'city':'College Station'});
	currentArray.append({'name':'Vader Conroe', 'link':'/mosaic/3834', 'city':'Conroe'});
	currentArray.append({'name':'Thousand-Yard Stare', 'link':'/mosaic/23800', 'city':'Odessa'});
	currentArray.append({'name':'Follow the Path to Guess More Glyphs', 'link':'/mosaic/23912', 'city':'San Antonio'});
	currentArray.append({'name':'Follow the Path to Guess the Glyph', 'link':'/mosaic/5502', 'city':'San Antonio'});
	currentArray.append({'name':'Resist It All', 'link':'/mosaic/24764', 'city':'Houston'});
	currentArray.append({'name':'Release the Kraken', 'link':'/mosaic/22417', 'city':'Groves'});
	currentArray.append({'name':'The_Key', 'link':'/mosaic/22644', 'city':'Houston'});
	currentArray.append({'name':'Walking Into The Rainbow', 'link':'/mosaic/25728', 'city':'Houston'});
	currentArray.append({'name':'All The Things', 'link':'/mosaic/24498', 'city':'Houston'});
	currentArray.append({'name':'Self-Similar Across Scale', 'link':'/mosaic/25227', 'city':'Houston'});

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
