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
	
	currentArray.append({'name':'Charlotte Airport (CLT)', 'link':'/mosaic/6997', 'city':'Charlotte'});
	currentArray.append({'name':'Durant Nature Park Hack', 'link':'/mosaic/19654', 'city':'Raleigh'});
	currentArray.append({'name':'Tour of Wingate University', 'link':'/mosaic/21543', 'city':'Wingate'});
	currentArray.append({'name':'The Good  the Bad  and the Ugly', 'link':'/mosaic/22092', 'city':'Matthews'});
	currentArray.append({'name':'Capture the Xixch', 'link':'/mosaic/27749', 'city':'Indian Trail'});
	currentArray.append({'name':'Upgrader', 'link':'/mosaic/18765', 'city':'Greenville'});
	currentArray.append({'name':'Ballantyne Elementals', 'link':'/mosaic/18832', 'city':'Pineville'});
	currentArray.append({'name':'Ballantyne and Morrison', 'link':'/mosaic/19059', 'city':'Charlotte'});
	currentArray.append({'name':'Paths of Greensboro', 'link':'/mosaic/19674', 'city':'Greensboro'});
	currentArray.append({'name':'Fun and Games at Squirrel Lake Park', 'link':'/mosaic/22638', 'city':'Matthews'});
	currentArray.append({'name':'RUCKgress', 'link':'/mosaic/23705', 'city':'Fayetteville'});
	currentArray.append({'name':'Show No Mercy', 'link':'/mosaic/23706', 'city':'Hope Mills'});
	currentArray.append({'name':'The Path of Totality', 'link':'/mosaic/25002', 'city':'Charlotte'});
	currentArray.append({'name':'R T (Resistance Training)', 'link':'/mosaic/26396', 'city':'Fletcher'});
	currentArray.append({'name':'Hunt with the Huntress - Asheville  NC', 'link':'/mosaic/19610', 'city':'Asheville'});
	currentArray.append({'name':'Understanding Your Ores', 'link':'/mosaic/19673', 'city':'Greensboro'});
	currentArray.append({'name':'C4  Coastal Carolina Community College', 'link':'/mosaic/20297', 'city':'Jacksonville'});
	currentArray.append({'name':'Glyph Message', 'link':'/mosaic/21484', 'city':'Goldsboro'});
	currentArray.append({'name':'Feelin FROGGY', 'link':'/mosaic/3096', 'city':'Currie'});
	currentArray.append({'name':'Visit Asheville', 'link':'/mosaic/3487', 'city':'Asheville'});
	currentArray.append({'name':'Get your ruck  get your bricks   get ruckin', 'link':'/mosaic/3770', 'city':'Fayetteville'});
	currentArray.append({'name':'Search for Jarvis', 'link':'/mosaic/5190', 'city':'Charlotte'});
	currentArray.append({'name':'Lenoir Mosaic', 'link':'/mosaic/5479', 'city':'Lenoir'});
	currentArray.append({'name':'Wake Forest', 'link':'/mosaic/6631', 'city':'Wake Forest'});
	currentArray.append({'name':'CANES', 'link':'/mosaic/7864', 'city':'Raleigh'});
	currentArray.append({'name':'Knightdale', 'link':'/mosaic/8736', 'city':'Knightdale'});
	currentArray.append({'name':'Hurricanes and Checkers', 'link':'/mosaic/10397', 'city':'Hickory'});
	currentArray.append({'name':'Historic Kernersville', 'link':'/mosaic/11513', 'city':'Kernersville'});
	currentArray.append({'name':'Sights in Downtown Cary', 'link':'/mosaic/12141', 'city':'Cary'});
	currentArray.append({'name':'Wilson NC', 'link':'/mosaic/12304', 'city':'Wilson'});
	currentArray.append({'name':'Geeky Dice', 'link':'/mosaic/13879', 'city':'Raleigh'});
	currentArray.append({'name':'Hunt For Jarvis', 'link':'/mosaic/13881', 'city':'Raleigh'});
	currentArray.append({'name':'Smurfs United - Smithfield', 'link':'/mosaic/13882', 'city':'Smithfield'});
	currentArray.append({'name':'Smurfs United - Clayton', 'link':'/mosaic/13883', 'city':'Clayton'});
	currentArray.append({'name':'Forest City Christmas Festival', 'link':'/mosaic/14497', 'city':'Forest City'});
	currentArray.append({'name':'Fix Bayonets', 'link':'/mosaic/16982', 'city':'Fort Bragg'});
	currentArray.append({'name':'OBX  NC', 'link':'/mosaic/18752', 'city':'Kill Devil Hills'});
	currentArray.append({'name':'Corolla Island Bridge', 'link':'/mosaic/18759', 'city':'Corolla'});
	currentArray.append({'name':'GVEGAS (Blue version)', 'link':'/mosaic/18762', 'city':'Greenville'});
	currentArray.append({'name':'GVEGAS (Green version)', 'link':'/mosaic/18763', 'city':'Winterville'});
	currentArray.append({'name':'Goldsboro  NC', 'link':'/mosaic/18769', 'city':'Goldsboro'});
	currentArray.append({'name':'Pullen Park', 'link':'/mosaic/18820', 'city':'Raleigh'});
	currentArray.append({'name':'Earn your Shelby badges', 'link':'/mosaic/18833', 'city':'Shelby'});
	currentArray.append({'name':'Wreaths Galore', 'link':'/mosaic/18834', 'city':'Shelby'});
	currentArray.append({'name':'Elements of Iredell', 'link':'/mosaic/19333', 'city':'Mooresville'});
	currentArray.append({'name':'Adorable Circle of Life', 'link':'/mosaic/20302', 'city':'Wake Forest'});
	currentArray.append({'name':'The Battle of Bunker Hill', 'link':'/mosaic/20336', 'city':'Colfax'});
	currentArray.append({'name':'Hacking Morrisville Parkway', 'link':'/mosaic/21508', 'city':'Morrisville'});
	currentArray.append({'name':'Churches in Glass', 'link':'/mosaic/22093', 'city':'Charlotte'});
	currentArray.append({'name':'William B  Umstead', 'link':'/mosaic/22253', 'city':'Raleigh'});
	currentArray.append({'name':'Where my hack is at', 'link':'/mosaic/23681', 'city':'Raleigh'});
	currentArray.append({'name':'Badger Mushroom Snake', 'link':'/mosaic/24571', 'city':'Durham'});
	currentArray.append({'name':'What s With W', 'link':'/mosaic/25004', 'city':'Waxhaw'});
	currentArray.append({'name':'Blue Valkyrie s Gauntlets', 'link':'/mosaic/27726', 'city':'Charlotte'});
	currentArray.append({'name':'OFFICE SPACE Mission Series', 'link':'/mosaic/27727', 'city':'Charlotte'});
	currentArray.append({'name':'Exploring Ocracoke', 'link':'/mosaic/27793', 'city':'Ocracoke'});
	currentArray.append({'name':'Professor Green', 'link':'/mosaic/18831', 'city':'Charlotte'});
	currentArray.append({'name':'Faces of Charlotte NoDa', 'link':'/mosaic/15029', 'city':'Charlotte'});
	currentArray.append({'name':'Faces of Charlotte Plaza Midwood', 'link':'/mosaic/15030', 'city':'Charlotte'});
	currentArray.append({'name':'NC Zoo Series', 'link':'/mosaic/18873', 'city':'Asheboro'});
	currentArray.append({'name':'SuckItBlue', 'link':'/mosaic/18764', 'city':'Greenville'});
	currentArray.append({'name':'Parks and Recreation', 'link':'/mosaic/3771', 'city':'Fayetteville'});
	currentArray.append({'name':'The Doctor', 'link':'/mosaic/5480', 'city':'Boone'});
	currentArray.append({'name':'Plenty to see in Greensboro', 'link':'/mosaic/5948', 'city':'Greensboro'});
	currentArray.append({'name':'CFBG X-FACTION', 'link':'/mosaic/7042', 'city':'Fayetteville'});
	currentArray.append({'name':'Battle For Bragg', 'link':'/mosaic/7437', 'city':'Fort Bragg'});
	currentArray.append({'name':'Lumber River', 'link':'/mosaic/7734', 'city':'Lumberton'});
	currentArray.append({'name':'WWC Series', 'link':'/mosaic/8481', 'city':'Swannanoa'});
	currentArray.append({'name':'PEACE  HOPE  SMOKE  POPE and INGRESS', 'link':'/mosaic/9727', 'city':'Fort Bragg'});
	currentArray.append({'name':'Wrightsville Beach  NC', 'link':'/mosaic/9757', 'city':'Wrightsville Beach'});
	currentArray.append({'name':'Daft Punk', 'link':'/mosaic/11514', 'city':'Walnut Cove'});
	currentArray.append({'name':'Lewisville Tour', 'link':'/mosaic/11875', 'city':'Lewisville'});
	currentArray.append({'name':'Halloween 2015 in Raleigh  NC', 'link':'/mosaic/13880', 'city':'Raleigh'});
	currentArray.append({'name':'Take a Ride In Pittsboro  NC', 'link':'/mosaic/15319', 'city':'Pittsboro'});
	currentArray.append({'name':'Twelve Cats of Christmas', 'link':'/mosaic/16981', 'city':'Fayetteville'});
	currentArray.append({'name':'Dark Side of the Triforce', 'link':'/mosaic/19630', 'city':'Raleigh'});
	currentArray.append({'name':'Lake Lynn', 'link':'/mosaic/19633', 'city':'Raleigh'});
	currentArray.append({'name':'Steal the Crown', 'link':'/mosaic/19837', 'city':'Charlotte'});
	currentArray.append({'name':'Law Enforcement in Mecklenburg County Patch Collection Mission Series', 'link':'/mosaic/27548', 'city':'Charlotte'});
	currentArray.append({'name':'Explore Asheville', 'link':'/mosaic/542', 'city':'Asheville'});
	currentArray.append({'name':'Hope Mills  Norh Carolina', 'link':'/mosaic/3769', 'city':'Hope Mills'});
	currentArray.append({'name':'Raleigh Skyline', 'link':'/mosaic/4988', 'city':'Raleigh'});
	currentArray.append({'name':'Forest City Christmas Lights', 'link':'/mosaic/5478', 'city':'Bostic'});
	currentArray.append({'name':'Monster Mash', 'link':'/mosaic/6994', 'city':'Matthews'});
	currentArray.append({'name':'Farming Elon University', 'link':'/mosaic/7789', 'city':'Elon'});
	currentArray.append({'name':'WF Seminary', 'link':'/mosaic/8498', 'city':'Wake Forest'});
	currentArray.append({'name':'Welcome to Charlotte', 'link':'/mosaic/8517', 'city':'Charlotte'});
	currentArray.append({'name':'ILM Banner Mission 1', 'link':'/mosaic/8650', 'city':'Wilmington'});
	currentArray.append({'name':'I like calling NC home', 'link':'/mosaic/9522', 'city':'Lincolnton'});
	currentArray.append({'name':'Welcome to the Crystal Coast', 'link':'/mosaic/11872', 'city':'Swansboro'});
	currentArray.append({'name':'Bond Park', 'link':'/mosaic/13569', 'city':'Cary'});
	currentArray.append({'name':'Historic Beaufort', 'link':'/mosaic/13741', 'city':'Beaufort'});
	currentArray.append({'name':'Love  Art and  60s Music', 'link':'/mosaic/13877', 'city':'Raleigh'});
	currentArray.append({'name':'Eastside Pride', 'link':'/mosaic/15026', 'city':'Charlotte'});
	currentArray.append({'name':'Dino-KNIGHT', 'link':'/mosaic/16678', 'city':'Gastonia'});
	currentArray.append({'name':'Stray Cat Strut', 'link':'/mosaic/17453', 'city':'Fayetteville'});
	currentArray.append({'name':'On the Hunt', 'link':'/mosaic/17454', 'city':'Fayetteville'});
	currentArray.append({'name':'Where Eagles Dare', 'link':'/mosaic/18767', 'city':'Hope Mills'});
	currentArray.append({'name':'Dean and Mike', 'link':'/mosaic/18768', 'city':'Chapel Hill'});
	currentArray.append({'name':'Chantilly Blue', 'link':'/mosaic/20940', 'city':'Charlotte'});
	currentArray.append({'name':'Floral Enlightenment', 'link':'/mosaic/21244', 'city':'Durham'});
	currentArray.append({'name':'I Dig Graveyards', 'link':'/mosaic/21248', 'city':'Raleigh'});
	currentArray.append({'name':'Touched by His Noodly Appendage (TbHNA)', 'link':'/mosaic/21426', 'city':'Durham'});
	currentArray.append({'name':'Magnus Reawakens Luminescent Heart Charlotte', 'link':'/mosaic/22187', 'city':'Charlotte'});
	currentArray.append({'name':'Creation', 'link':'/mosaic/22873', 'city':'Fayetteville'});
	currentArray.append({'name':'We re All Mad Here', 'link':'/mosaic/22874', 'city':'Fayetteville'});
	currentArray.append({'name':'Gas Giant', 'link':'/mosaic/25003', 'city':'Charlotte'});
	currentArray.append({'name':'Goldsboro NC Home of Seymour Johnson AFB', 'link':'/mosaic/25313', 'city':'Goldsboro'});
	currentArray.append({'name':'Queen Anne s Revenge', 'link':'/mosaic/25330', 'city':'Kill Devil Hills'});
	currentArray.append({'name':'Knight Life', 'link':'/mosaic/25516', 'city':'Fayetteville'});
	currentArray.append({'name':'New Bern  NC Waterfront', 'link':'/mosaic/25575', 'city':'New Bern'});
	currentArray.append({'name':'Ride the Lightning', 'link':'/mosaic/25966', 'city':'Fayetteville'});
	currentArray.append({'name':'Cold-Blooded', 'link':'/mosaic/26273', 'city':'Hope Mills'});
	currentArray.append({'name':'Night Rising', 'link':'/mosaic/26296', 'city':'Fayetteville'});
	currentArray.append({'name':'Green  and  Blue', 'link':'/mosaic/26311', 'city':'Dunn'});
	currentArray.append({'name':'Bye Felicia', 'link':'/mosaic/1486', 'city':'Wilmington'});
	currentArray.append({'name':'Heart of Fayetteville', 'link':'/mosaic/4140', 'city':'Fayetteville'});
	currentArray.append({'name':'Greetings From Fayetteville  NC', 'link':'/mosaic/5879', 'city':'Fayetteville'});
	currentArray.append({'name':'Wolfpack Pride (Part 1 of 24)', 'link':'/mosaic/8648', 'city':'Raleigh'});
	currentArray.append({'name':'1-Greetings from Wilmington N C', 'link':'/mosaic/8649', 'city':'Wilmington'});
	currentArray.append({'name':'Burnin  Mods', 'link':'/mosaic/11512', 'city':'Winston-Salem'});
	currentArray.append({'name':'When Dinosaurs Ruled The Sky', 'link':'/mosaic/12788', 'city':'Cary'});
	currentArray.append({'name':'Psycho-Delic Frog', 'link':'/mosaic/21486', 'city':'Fayetteville'});
	currentArray.append({'name':'WF Panda Explosion', 'link':'/mosaic/24570', 'city':'Wake Forest'});
	currentArray.append({'name':'Praise the sun', 'link':'/mosaic/26050', 'city':'Youngsville, Franklinton, Henderson, Oxford'});
	currentArray.append({'name':'Queen CLT Uptown Series', 'link':'/mosaic/3584', 'city':'Charlotte'});
	currentArray.append({'name':'Duke Tour', 'link':'/mosaic/5717', 'city':'Durham'});
	currentArray.append({'name':'Hacking Wonderland', 'link':'/mosaic/5880', 'city':'Fayetteville'});
	currentArray.append({'name':'DTD Grand Tour', 'link':'/mosaic/7731', 'city':'Durham'});
	currentArray.append({'name':'Cherry Blossoms', 'link':'/mosaic/7894', 'city':'Raleigh'});
	currentArray.append({'name':'All-American City Tour', 'link':'/mosaic/8651', 'city':'Fayetteville'});
	currentArray.append({'name':'Papa Viking', 'link':'/mosaic/8960', 'city':'Raleigh'});
	currentArray.append({'name':'Angel of Death', 'link':'/mosaic/14058', 'city':'Pope Field'});
	currentArray.append({'name':'Charlotte Enlightened', 'link':'/mosaic/3345', 'city':'Marshville'});
	currentArray.append({'name':'This is Halloween', 'link':'/mosaic/5438', 'city':'Raleigh'});
	currentArray.append({'name':'Wolf', 'link':'/mosaic/9521', 'city':'Raleigh'});
	currentArray.append({'name':'Lord of the Gardens', 'link':'/mosaic/25334', 'city':'Fayetteville'});
	currentArray.append({'name':'Charlotte Fire Department Station Patch Collection Mission Series', 'link':'/mosaic/27547', 'city':'Charlotte'});
	currentArray.append({'name':'Lantern Corps', 'link':'/mosaic/24576', 'city':'Raleigh'});

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
