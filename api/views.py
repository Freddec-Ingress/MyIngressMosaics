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
	
	currentArray.append({'name':'Clinton Hill Golf Course', 'link':'/mosaic/7926', 'city':' Belleville'});
	currentArray.append({'name':'Gordon F  Moore Park', 'link':'/mosaic/18858', 'city':' Alton'});
	currentArray.append({'name':'Old Maud  Ghost of the PLZW Railroad', 'link':'/mosaic/21510', 'city':' Palatine'});
	currentArray.append({'name':'Freeport Miniseries', 'link':'/mosaic/4464', 'city':' Baileyville'});
	currentArray.append({'name':'Explore Dupo IL', 'link':'/mosaic/4750', 'city':' Dupo'});
	currentArray.append({'name':'The Rock River Rec Bike Path', 'link':'/mosaic/10593', 'city':' Rockford'});
	currentArray.append({'name':'Oak Park Borderlands', 'link':'/mosaic/19479', 'city':' Elmwood Park'});
	currentArray.append({'name':'Des Plaines River Trail North', 'link':'/mosaic/20063', 'city':' Wheeling'});
	currentArray.append({'name':'SIUE Sequential Missions', 'link':'/mosaic/20840', 'city':' Edwardsville'});
	currentArray.append({'name':'Caton Farm Banner', 'link':'/mosaic/2987', 'city':' Plainfield'});
	currentArray.append({'name':'Oregon  IL October 2015 FS', 'link':'/mosaic/3286', 'city':' Oregon'});
	currentArray.append({'name':'Centennial Park', 'link':'/mosaic/3338', 'city':' Lincolnwood'});
	currentArray.append({'name':'Pilsen 6', 'link':'/mosaic/4037', 'city':' Chicago'});
	currentArray.append({'name':'Peoria riverfront skyline art', 'link':'/mosaic/4997', 'city':' Peoria'});
	currentArray.append({'name':'Belleville IL', 'link':'/mosaic/5795', 'city':' Belleville'});
	currentArray.append({'name':'I-L-L   I-N-I', 'link':'/mosaic/5826', 'city':' Urbana'});
	currentArray.append({'name':'Quest for the Golden Pepe', 'link':'/mosaic/5828', 'city':' Champaign'});
	currentArray.append({'name':'Normal Mission Series', 'link':'/mosaic/6057', 'city':' Normal'});
	currentArray.append({'name':'Welcome to Wauconda', 'link':'/mosaic/6235', 'city':' Mundelein'});
	currentArray.append({'name':'FVE Geneva Commons', 'link':'/mosaic/7121', 'city':' Geneva'});
	currentArray.append({'name':'Downtown DeKalb Banner', 'link':'/mosaic/9039', 'city':' DeKalb'});
	currentArray.append({'name':'Huskies on Parade C', 'link':'/mosaic/9223', 'city':' Sycamore'});
	currentArray.append({'name':'Huskies on Parade H', 'link':'/mosaic/9224', 'city':' Sycamore'});
	currentArray.append({'name':'GET YR BANNER ON', 'link':'/mosaic/9690', 'city':' Urbana'});
	currentArray.append({'name':'Think Spring  Nature Center', 'link':'/mosaic/9840', 'city':' Schaumburg'});
	currentArray.append({'name':'Hacking Lincoln s Benches', 'link':'/mosaic/9848', 'city':' Springfield'});
	currentArray.append({'name':'Southern Illinois University at Carbondale 1', 'link':'/mosaic/11095', 'city':' Carbondale'});
	currentArray.append({'name':'Lena Mission', 'link':'/mosaic/13810', 'city':' Lena'});
	currentArray.append({'name':'Villa Park  IL Prairie Path mission', 'link':'/mosaic/14043', 'city':' Lombard'});
	currentArray.append({'name':'Polish Patches', 'link':'/mosaic/15716', 'city':' Chicago'});
	currentArray.append({'name':'Empire on PLATO', 'link':'/mosaic/16361', 'city':' Urbana'});
	currentArray.append({'name':'Starved Rock', 'link':'/mosaic/20069', 'city':' Oglesby'});
	currentArray.append({'name':'Digbob - Morton', 'link':'/mosaic/20841', 'city':' Morton'});
	currentArray.append({'name':'Will County Seeltoads', 'link':'/mosaic/21459', 'city':' Romeoville'});
	currentArray.append({'name':'GET YR INGRESS ON', 'link':'/mosaic/21514', 'city':' Urbana'});
	currentArray.append({'name':'Explore Round Lake Illinois Hack Mural', 'link':'/mosaic/22246', 'city':' Round Lake'});
	currentArray.append({'name':'Norway Banner', 'link':'/mosaic/23689', 'city':' Sheridan'});
	currentArray.append({'name':'Harper Hack', 'link':'/mosaic/24746', 'city':' Palatine'});
	currentArray.append({'name':'Chicago Highlights', 'link':'/mosaic/24866', 'city':' Chicago'});
	currentArray.append({'name':'Color', 'link':'/mosaic/10946', 'city':' Champaign'});
	currentArray.append({'name':'Sister Streets', 'link':'/mosaic/20765', 'city':' St. Charles'});
	currentArray.append({'name':'Mystery Missions', 'link':'/mosaic/24421', 'city':' Aurora'});
	currentArray.append({'name':'ISU Banner Mission - Sports Arena', 'link':'/mosaic/2989', 'city':' Normal'});
	currentArray.append({'name':'Shrine Walk', 'link':'/mosaic/3277', 'city':' Belleville'});
	currentArray.append({'name':'Hack About Galesburg', 'link':'/mosaic/3285', 'city':' Galesburg'});
	currentArray.append({'name':'Welcome to Buffalo Grove', 'link':'/mosaic/5945', 'city':' Buffalo Grove'});
	currentArray.append({'name':'Welcome to Lake Zurich', 'link':'/mosaic/5967', 'city':' Lake Zurich'});
	currentArray.append({'name':'Beta Missions', 'link':'/mosaic/8811', 'city':' Arlington Heights'});
	currentArray.append({'name':'Blue Skies in AH', 'link':'/mosaic/8825', 'city':' Arlington Heights'});
	currentArray.append({'name':'Cornfest', 'link':'/mosaic/8903', 'city':' DeKalb'});
	currentArray.append({'name':'Downtown Bloomington Panorama', 'link':'/mosaic/9038', 'city':' Bloomington'});
	currentArray.append({'name':'Rockford University', 'link':'/mosaic/10158', 'city':' Rockford'});
	currentArray.append({'name':'Ride The Bus System', 'link':'/mosaic/11284', 'city':' Champaign'});
	currentArray.append({'name':'Fox Valley Resistance', 'link':'/mosaic/11635', 'city':' Elgin'});
	currentArray.append({'name':'Chicago Style', 'link':'/mosaic/14967', 'city':' Chicago'});
	currentArray.append({'name':'Via Noir - Darkside Of XM', 'link':'/mosaic/15261', 'city':' Chicago'});
	currentArray.append({'name':'Jefferson St Hobo Train', 'link':'/mosaic/17181', 'city':' Shorewood'});
	currentArray.append({'name':'Historic McHenry  IL', 'link':'/mosaic/17802', 'city':' McHenry'});
	currentArray.append({'name':'Chicago River North', 'link':'/mosaic/20588', 'city':' Chicago'});
	currentArray.append({'name':'Lincoln Highway Resistance Series', 'link':'/mosaic/24471', 'city':' Chicago Heights'});
	currentArray.append({'name':'Chicago Blues', 'link':'/mosaic/26838', 'city':' Chicago'});
	currentArray.append({'name':'Explore Southern Illinois University', 'link':'/mosaic/1443', 'city':' Carbondale'});
	currentArray.append({'name':'Windy City', 'link':'/mosaic/1651', 'city':' Chicago'});
	currentArray.append({'name':'Red Faction', 'link':'/mosaic/3007', 'city':' Lockport'});
	currentArray.append({'name':'ENL and RES banner mission', 'link':'/mosaic/3516', 'city':' Elmhurst'});
	currentArray.append({'name':'Freeport Mission Series', 'link':'/mosaic/4219', 'city':' Freeport'});
	currentArray.append({'name':'Roland Jarvis', 'link':'/mosaic/5188', 'city':' Wheeling'});
	currentArray.append({'name':'Grand Tower to Cairo', 'link':'/mosaic/5804', 'city':' Grand Tower'});
	currentArray.append({'name':'UIUC Assembly Hall Banner', 'link':'/mosaic/5939', 'city':' Urbana'});
	currentArray.append({'name':'Loyola Ramblers', 'link':'/mosaic/6394', 'city':' Chicago'});
	currentArray.append({'name':'St Clair County', 'link':'/mosaic/7439', 'city':' Belleville'});
	currentArray.append({'name':'Kankakee County Tour', 'link':'/mosaic/9784', 'city':' Kankakee'});
	currentArray.append({'name':'Northern Illinois University', 'link':'/mosaic/10057', 'city':' DeKalb'});
	currentArray.append({'name':'The Acolyte', 'link':'/mosaic/10090', 'city':' Des Plaines'});
	currentArray.append({'name':'Historic Champaign Banner', 'link':'/mosaic/11662', 'city':' Champaign'});
	currentArray.append({'name':'+1  Banner of Leveling', 'link':'/mosaic/13199', 'city':' Champaign'});
	currentArray.append({'name':'Morton Arboretum', 'link':'/mosaic/13406', 'city':' Lombard'});
	currentArray.append({'name':'Enlightenment of the Near North Burbs', 'link':'/mosaic/13832', 'city':' Skokie'});
	currentArray.append({'name':'Joliet Order of the Link Amp', 'link':'/mosaic/14844', 'city':' Joliet'});
	currentArray.append({'name':'Thorgi', 'link':'/mosaic/14845', 'city':' Plainfield'});
	currentArray.append({'name':'Chicago Noir 2016', 'link':'/mosaic/15715', 'city':' Chicago'});
	currentArray.append({'name':'Via Noir Chicago', 'link':'/mosaic/15791', 'city':' Chicago'});
	currentArray.append({'name':'MissionDay Chicago - (13-11-2016)', 'link':'/mosaic/15807', 'city':' Chicago'});
	currentArray.append({'name':'Battle for the Shrine', 'link':'/mosaic/16098', 'city':' Belleville'});
	currentArray.append({'name':'A Night in Rock Island', 'link':'/mosaic/16363', 'city':' Rock Island'});
	currentArray.append({'name':'Millennium Park', 'link':'/mosaic/16500', 'city':' Chicago'});
	currentArray.append({'name':'Joliet Binary Banner', 'link':'/mosaic/16988', 'city':' Joliet'});
	currentArray.append({'name':'UCR - Elmhurst College Southeast Commons', 'link':'/mosaic/17092', 'city':' Elmhurst'});
	currentArray.append({'name':'UIC 1st comic  trip', 'link':'/mosaic/18889', 'city':' Chicago'});
	currentArray.append({'name':'Yorkville', 'link':'/mosaic/19281', 'city':' Yorkville'});
	currentArray.append({'name':'Northbrook Based ENL RES Hack Mural', 'link':'/mosaic/22248', 'city':' Northbrook'});
	currentArray.append({'name':'Derping Bolingbrook', 'link':'/mosaic/22316', 'city':' Bolingbrook'});
	currentArray.append({'name':'The Ridge Traveler', 'link':'/mosaic/23025', 'city':' Lansing'});
	currentArray.append({'name':'Mark of the Crimson King', 'link':'/mosaic/25120', 'city':' Lansing'});
	currentArray.append({'name':'MD Chicago 2017', 'link':'/mosaic/25282', 'city':' Chicago'});
	currentArray.append({'name':'DTC Banner', 'link':'/mosaic/25535', 'city':' Champaign'});
	currentArray.append({'name':'Ecto Highland Park', 'link':'/mosaic/25538', 'city':' Highland Park'});
	currentArray.append({'name':'Sly Like A Fox', 'link':'/mosaic/25590', 'city':' Champaign'});
	currentArray.append({'name':'Woodstock', 'link':'/mosaic/26281', 'city':' Woodstock'});
	currentArray.append({'name':'Where s Waldo', 'link':'/mosaic/26542', 'city':' Joliet'});
	currentArray.append({'name':'Fall Frolic at Ty Warner Park', 'link':'/mosaic/26845', 'city':' Westmont'});
	currentArray.append({'name':'Waukegan  IL Banner Mission', 'link':'/mosaic/27942', 'city':' Waukegan'});
	currentArray.append({'name':'Smurf the Earth 2017 - Illinois', 'link':'/mosaic/21975', 'city':' Belleville'});
	currentArray.append({'name':'Logan Square Centennial Banner', 'link':'/mosaic/3508', 'city':' Chicago'});
	currentArray.append({'name':'Illinois State Capitol', 'link':'/mosaic/9244', 'city':' Springfield'});
	currentArray.append({'name':'Does it still play in Peoria', 'link':'/mosaic/9545', 'city':' Peoria'});
	currentArray.append({'name':'Ninian Edwards', 'link':'/mosaic/13267', 'city':' Edwardsville'});
	currentArray.append({'name':'Chicago Botanic Garden Tour', 'link':'/mosaic/16792', 'city':' Glencoe'});
	currentArray.append({'name':'Fireworks at Ty Warner Park', 'link':'/mosaic/18472', 'city':' Westmont'});
	currentArray.append({'name':'The Cloud Gate', 'link':'/mosaic/21256', 'city':' Chicago'});
	currentArray.append({'name':'Chicago s Merchandise Mart', 'link':'/mosaic/25623', 'city':' Chicago'});
	currentArray.append({'name':'Thrown For a Loop', 'link':'/mosaic/26192', 'city':' Chicago'});
	currentArray.append({'name':'Wrong Crystal Lake', 'link':'/mosaic/26316', 'city':' Crystal Lake'});
	currentArray.append({'name':'Alphabet in Champaign', 'link':'/mosaic/19080', 'city':' Champaign'});
	currentArray.append({'name':'Chicago Skyline', 'link':'/mosaic/4994', 'city':' Chicago'});
	currentArray.append({'name':'Goblin', 'link':'/mosaic/9136', 'city':' Quincy'});
	currentArray.append({'name':'Rockford River', 'link':'/mosaic/9271', 'city':' Loves Park'});
	currentArray.append({'name':'Galena Gets a Banner', 'link':'/mosaic/9842', 'city':' Galena'});
	currentArray.append({'name':'Route 66 Illinois Lincoln to St  Louis', 'link':'/mosaic/18696', 'city':' Lincoln'});
	currentArray.append({'name':'R66-IL1 - Chicago to Atlanta', 'link':'/mosaic/21254', 'city':' Chicago'});
	currentArray.append({'name':'Enlightenment Mission', 'link':'/mosaic/3365', 'city':' Deerfield'});
	currentArray.append({'name':'Elgin Mission', 'link':'/mosaic/5665', 'city':' Elgin'});
	currentArray.append({'name':'Quincy s Bayview Bridge', 'link':'/mosaic/12917', 'city':' Quincy'});

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
