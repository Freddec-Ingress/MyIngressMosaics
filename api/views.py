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
	
	currentArray.append({'name':'Katy Trail Missions', 'link':'/mosaic/76', 'city':'Dallas'});
	currentArray.append({'name':'Welcome to Wallis', 'link':'/mosaic/10749', 'city':'Wallis'});
	currentArray.append({'name':'Tower of the Americas', 'link':'/mosaic/10769', 'city':'San Antonio'});
	currentArray.append({'name':'Houston Zoo Mini-Mission', 'link':'/mosaic/17239', 'city':'Houston'});
	currentArray.append({'name':'Drop Into Bastrop', 'link':'/mosaic/18487', 'city':'Bastrop'});
	currentArray.append({'name':'City of Newton Tour', 'link':'/mosaic/18906', 'city':'Newton'});
	currentArray.append({'name':'FROG and CORPUS', 'link':'/mosaic/18908', 'city':'Corpus Christi'});
	currentArray.append({'name':'Monuments of Forest Lawn', 'link':'/mosaic/20167', 'city':'Beaumont'});
	currentArray.append({'name':'Memorial Streetlamps in Groesbeck TX', 'link':'/mosaic/20717', 'city':'Groesbeck'});
	currentArray.append({'name':'Congress Landmarks', 'link':'/mosaic/24717', 'city':'Austin'});
	currentArray.append({'name':'Fort Worth Abaddon Clusters', 'link':'/mosaic/77', 'city':'Fort Worth'});
	currentArray.append({'name':'Victoria City Hack Mission', 'link':'/mosaic/8566', 'city':'Victoria'});
	currentArray.append({'name':'Pflugerville Heritage Tour', 'link':'/mosaic/9504', 'city':'Pflugerville'});
	currentArray.append({'name':'CorsiCANA', 'link':'/mosaic/17700', 'city':'Corsicana'});
	currentArray.append({'name':'Shōnin Austin Clusters', 'link':'/mosaic/19492', 'city':'Austin'});
	currentArray.append({'name':'13Magnus-Dallas Clusters', 'link':'/mosaic/19494', 'city':'Dallas'});
	currentArray.append({'name':'Recursion Austin Clusters', 'link':'/mosaic/19497', 'city':'Austin'});
	currentArray.append({'name':'Klein Park and Welcome to Beaumont', 'link':'/mosaic/20329', 'city':'Beaumont'});
	currentArray.append({'name':'Wabbit Hunting', 'link':'/mosaic/17214', 'city':'Odessa'});
	currentArray.append({'name':'Historic Route 66', 'link':'/mosaic/18780', 'city':'Amarillo'});
	currentArray.append({'name':'The Walking Dead - Austin', 'link':'/mosaic/19400', 'city':'Austin'});
	currentArray.append({'name':'Music Park', 'link':'/mosaic/19592', 'city':'New York'});
	currentArray.append({'name':'Smurf Tears in GP', 'link':'/mosaic/20145', 'city':'Grand Prairie'});
	currentArray.append({'name':'Rainbow Hearts', 'link':'/mosaic/24961', 'city':'Houston'});
	currentArray.append({'name':'Abilene Christian University', 'link':'/mosaic/2303', 'city':'Abilene'});
	currentArray.append({'name':'Banana Adventures', 'link':'/mosaic/2340', 'city':'Garland'});
	currentArray.append({'name':'Happy Flight', 'link':'/mosaic/2360', 'city':'McKinney'});
	currentArray.append({'name':'McKinney Maniac Adventures', 'link':'/mosaic/2361', 'city':'McKinney'});
	currentArray.append({'name':'Dragon Dance', 'link':'/mosaic/2378', 'city':'Plano'});
	currentArray.append({'name':'FRISCO', 'link':'/mosaic/2484', 'city':'Frisco'});
	currentArray.append({'name':'austiN neon', 'link':'/mosaic/3240', 'city':'Austin'});
	currentArray.append({'name':'The Order of the Link Amp - Downtown Austin', 'link':'/mosaic/3241', 'city':'Austin'});
	currentArray.append({'name':'BCSE College Station', 'link':'/mosaic/3249', 'city':'College Station'});
	currentArray.append({'name':'Fielding Ops', 'link':'/mosaic/3256', 'city':'College Station'});
	currentArray.append({'name':'Welcome to woodville', 'link':'/mosaic/3258', 'city':'Woodville'});
	currentArray.append({'name':'Trail of Wildflowers', 'link':'/mosaic/3268', 'city':'Savoy'});
	currentArray.append({'name':'Equality', 'link':'/mosaic/4263', 'city':'Dallas'});
	currentArray.append({'name':'You ll Love Katy', 'link':'/mosaic/4757', 'city':'Katy'});
	currentArray.append({'name':'Glyph Austin', 'link':'/mosaic/4976', 'city':'Austin'});
	currentArray.append({'name':'Go Lions', 'link':'/mosaic/5796', 'city':'Commerce'});
	currentArray.append({'name':'Welcome to Sweetwater', 'link':'/mosaic/6197', 'city':'Sweetwater'});
	currentArray.append({'name':'Angelo State Tour', 'link':'/mosaic/6351', 'city':'San Angelo'});
	currentArray.append({'name':'Texas City Churches', 'link':'/mosaic/6620', 'city':'Texas City'});
	currentArray.append({'name':'Welcome to SFA', 'link':'/mosaic/6622', 'city':'Nacogdoches'});
	currentArray.append({'name':'Canton  Texas', 'link':'/mosaic/6624', 'city':'Canton'});
	currentArray.append({'name':'Explore the heart of Abilene  Texas', 'link':'/mosaic/6651', 'city':'Abilene'});
	currentArray.append({'name':'Corpus Scavenger Hunt', 'link':'/mosaic/7038', 'city':'Corpus Christi'});
	currentArray.append({'name':'Providence Village', 'link':'/mosaic/8975', 'city':'Aubrey'});
	currentArray.append({'name':'Downtown San Antonio Series', 'link':'/mosaic/9042', 'city':'San Antonio'});
	currentArray.append({'name':'Follow the Fun in Ft Worth', 'link':'/mosaic/9092', 'city':'Fort Worth'});
	currentArray.append({'name':'Glyph Corpus', 'link':'/mosaic/9134', 'city':'Corpus Christi'});
	currentArray.append({'name':'Here s to Adventure', 'link':'/mosaic/9190', 'city':'The Colony'});
	currentArray.append({'name':'Take a Spin around White Rock Lake', 'link':'/mosaic/9742', 'city':'Dallas'});
	currentArray.append({'name':'Cruising Commerce', 'link':'/mosaic/9847', 'city':'Commerce'});
	currentArray.append({'name':'The Mission of the Doctor', 'link':'/mosaic/9891', 'city':'Plano'});
	currentArray.append({'name':'Fairies', 'link':'/mosaic/10197', 'city':'Spring'});
	currentArray.append({'name':'Run  Run  Run', 'link':'/mosaic/10265', 'city':'Houston'});
	currentArray.append({'name':'The Void', 'link':'/mosaic/10286', 'city':'Humble'});
	currentArray.append({'name':'Tomball in Webdings', 'link':'/mosaic/10447', 'city':'Tomball'});
	currentArray.append({'name':'Monster Eyes', 'link':'/mosaic/10746', 'city':'Houston'});
	currentArray.append({'name':'The Celebration', 'link':'/mosaic/10748', 'city':'Corpus Christi'});
	currentArray.append({'name':'Devil Dancers', 'link':'/mosaic/10752', 'city':'Corpus Christi'});
	currentArray.append({'name':'A Day in Dallas', 'link':'/mosaic/12071', 'city':'Dallas'});
	currentArray.append({'name':'Helmet', 'link':'/mosaic/12460', 'city':'Carrollton'});
	currentArray.append({'name':'On  On Buffaloes', 'link':'/mosaic/12467', 'city':'Canyon'});
	currentArray.append({'name':'Texas Wildflowers - Bluebonnet', 'link':'/mosaic/12855', 'city':'Plano'});
	currentArray.append({'name':'San Antonio Texas Proud', 'link':'/mosaic/14041', 'city':'San Antonio'});
	currentArray.append({'name':'Tequila Flight', 'link':'/mosaic/14042', 'city':'Houston'});
	currentArray.append({'name':'The Battle for SCS', 'link':'/mosaic/14479', 'city':'College Station'});
	currentArray.append({'name':'Heavens Bells', 'link':'/mosaic/14782', 'city':'Houston'});
	currentArray.append({'name':'Dia de los Muertos', 'link':'/mosaic/14960', 'city':'San Antonio'});
	currentArray.append({'name':'Bob hall pier', 'link':'/mosaic/15310', 'city':'Corpus Christi'});
	currentArray.append({'name':'Cemetery - Tomball', 'link':'/mosaic/15786', 'city':'Tomball'});
	currentArray.append({'name':'WestTx', 'link':'/mosaic/16437', 'city':'Midland'});
	currentArray.append({'name':'Bones', 'link':'/mosaic/17139', 'city':'Katy'});
	currentArray.append({'name':'Sextet Moral Development', 'link':'/mosaic/17697', 'city':'Sherman'});
	currentArray.append({'name':'Sextet Changes', 'link':'/mosaic/17698', 'city':'Sherman'});
	currentArray.append({'name':'Path of the Jedi', 'link':'/mosaic/17699', 'city':'The Colony'});
	currentArray.append({'name':'Die Young - Amy Winehouse', 'link':'/mosaic/17706', 'city':'Dallas'});
	currentArray.append({'name':'Zaprange', 'link':'/mosaic/17756', 'city':'Midland'});
	currentArray.append({'name':'Spy vs Spy', 'link':'/mosaic/17841', 'city':'Houston'});
	currentArray.append({'name':'Carthage', 'link':'/mosaic/17870', 'city':'Carthage'});
	currentArray.append({'name':'Stupid', 'link':'/mosaic/18277', 'city':'College Station'});
	currentArray.append({'name':'LuvHuk', 'link':'/mosaic/18461', 'city':'Dallas'});
	currentArray.append({'name':'BAYLOR University', 'link':'/mosaic/18530', 'city':'Waco'});
	currentArray.append({'name':'Richland College', 'link':'/mosaic/18741', 'city':'Dallas'});
	currentArray.append({'name':'Glyph ALICE', 'link':'/mosaic/18888', 'city':'Alice'});
	currentArray.append({'name':'Peace in the World', 'link':'/mosaic/18967', 'city':'Salado'});
	currentArray.append({'name':'Rainbow Poptart Kitty', 'link':'/mosaic/19023', 'city':'Montgomery'});
	currentArray.append({'name':'The Enlightenment of the Jedi', 'link':'/mosaic/20129', 'city':'Frisco'});
	currentArray.append({'name':'Destruction By Design', 'link':'/mosaic/20298', 'city':'Longview'});
	currentArray.append({'name':'GoRuck Scavenger- SATX USA 25 March 2017', 'link':'/mosaic/20547', 'city':'San Antonio'});
	currentArray.append({'name':'Spring Creek Greenway Trail', 'link':'/mosaic/20904', 'city':'Humble'});
	currentArray.append({'name':'One of Us', 'link':'/mosaic/21002', 'city':'College Station'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart', 'link':'/mosaic/21109', 'city':'Houston'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Austin', 'link':'/mosaic/21112', 'city':'Austin'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart San Antonio', 'link':'/mosaic/21114', 'city':'San Antonio'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Corpus Christi', 'link':'/mosaic/21115', 'city':'Corpus Christi'});
	currentArray.append({'name':'Monuments of Magnolia', 'link':'/mosaic/21145', 'city':'Beaumont'});
	currentArray.append({'name':'Polk County Seat', 'link':'/mosaic/21146', 'city':'Livingston'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart-DFW', 'link':'/mosaic/21647', 'city':'Grapevine'});
	currentArray.append({'name':'Banner Mission in Canyon  TX', 'link':'/mosaic/21711', 'city':'Canyon'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart - Beaumont', 'link':'/mosaic/21907', 'city':'Beaumont'});
	currentArray.append({'name':'中井駅から最勝寺へ', 'link':'/mosaic/22300', 'city':'New York'});
	currentArray.append({'name':'ペルセポリスよもう一度', 'link':'/mosaic/22327', 'city':'New York'});
	currentArray.append({'name':'Happy New Year 2017 @ Shinjuku', 'link':'/mosaic/22328', 'city':'New York'});
	currentArray.append({'name':'SMILE', 'link':'/mosaic/22944', 'city':'Houston'});
	currentArray.append({'name':'Leander Lovelys', 'link':'/mosaic/23310', 'city':'Leander'});
	currentArray.append({'name':'POINT  COMFORT', 'link':'/mosaic/23325', 'city':'Point Comfort'});
	currentArray.append({'name':'臺鐵EUM400', 'link':'/mosaic/23345', 'city':'New York'});
	currentArray.append({'name':'Path of the Dark Side', 'link':'/mosaic/23792', 'city':'Plano'});
	currentArray.append({'name':'Come and Take It (Carrollton)', 'link':'/mosaic/24218', 'city':'Carrollton TX'});
	currentArray.append({'name':'Magnus Reawakens Luminescent Heart - Pf', 'link':'/mosaic/24492', 'city':'Pflugerville'});
	currentArray.append({'name':'Oilfield Country', 'link':'/mosaic/25446', 'city':'Odessa'});
	currentArray.append({'name':'#IFS Fort Worth XFAC BRO', 'link':'/mosaic/25746', 'city':'Fort Worth'});
	currentArray.append({'name':'Fort Worth Botanical Gardens', 'link':'/mosaic/27509', 'city':'Fort Worth'});
	currentArray.append({'name':'Tom Landry Mural', 'link':'/mosaic/27516', 'city':'Mission'});
	currentArray.append({'name':'Flock of Plano', 'link':'/mosaic/27708', 'city':'Plano'});

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
