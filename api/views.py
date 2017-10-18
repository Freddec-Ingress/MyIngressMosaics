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
	
	currentArray.append({'name':'Visit the town of COLFAX', 'link':'/mosaic/64', 'city':'Colfax'});
	currentArray.append({'name':'Emeryville Banner', 'link':'/mosaic/1111', 'city':'Emeryville'});
	currentArray.append({'name':'Excelsior San Francisco', 'link':'/mosaic/3370', 'city':'San Francisco'});
	currentArray.append({'name':'Webster Tour', 'link':'/mosaic/3371', 'city':'Alameda'});
	currentArray.append({'name':'SF Bart Rapid Transit Car', 'link':'/mosaic/3377', 'city':'San Francisco'});
	currentArray.append({'name':'Joe Philley Tribute Series', 'link':'/mosaic/3378', 'city':'Temecula'});
	currentArray.append({'name':'Resistance is Inevitable', 'link':'/mosaic/3391', 'city':'San Luis Obispo'});
	currentArray.append({'name':'Albany Bulb Art and Nature Walk', 'link':'/mosaic/3396', 'city':'Berkeley'});
	currentArray.append({'name':'Bike Trooper Series', 'link':'/mosaic/3401', 'city':'Seaside'});
	currentArray.append({'name':'Bro San Francisco', 'link':'/mosaic/3402', 'city':'San Francisco'});
	currentArray.append({'name':'Doyle Hollis', 'link':'/mosaic/3411', 'city':'Emeryville'});
	currentArray.append({'name':'Googleplex', 'link':'/mosaic/3416', 'city':'Mountain View'});
	currentArray.append({'name':'SF Botanical Garden', 'link':'/mosaic/3417', 'city':'San Francisco'});
	currentArray.append({'name':'GIANTS', 'link':'/mosaic/3432', 'city':'San Francisco'});
	currentArray.append({'name':'Glyph Master Oakland', 'link':'/mosaic/3434', 'city':'Oakland'});
	currentArray.append({'name':'JLS Build-A-Rainbow', 'link':'/mosaic/3438', 'city':'Oakland'});
	currentArray.append({'name':'View from the Top', 'link':'/mosaic/3443', 'city':'San Luis Obispo'});
	currentArray.append({'name':'Make Your Choice  Seaside', 'link':'/mosaic/3449', 'city':'Seaside'});
	currentArray.append({'name':'Moraga Meander', 'link':'/mosaic/3450', 'city':'Moraga'});
	currentArray.append({'name':'Niles Mission Series', 'link':'/mosaic/3452', 'city':'Fremont'});
	currentArray.append({'name':'Orinda Overview', 'link':'/mosaic/3454', 'city':'Orinda'});
	currentArray.append({'name':'SF Peak Walk', 'link':'/mosaic/3467', 'city':'San Francisco'});
	currentArray.append({'name':'Show your colors', 'link':'/mosaic/3468', 'city':'Santa Cruz'});
	currentArray.append({'name':'UCDAVIS', 'link':'/mosaic/3477', 'city':'Davis'});
	currentArray.append({'name':'WeHo Los Angeles', 'link':'/mosaic/3502', 'city':'Los Angeles'});
	currentArray.append({'name':'IRVINE', 'link':'/mosaic/3824', 'city':'Irvine'});
	currentArray.append({'name':'RANCHO', 'link':'/mosaic/3827', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'PORTAL Upland', 'link':'/mosaic/3828', 'city':'Upland'});
	currentArray.append({'name':'RESIST Rancho', 'link':'/mosaic/3829', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'Explore Malibu', 'link':'/mosaic/4261', 'city':'Malibu'});
	currentArray.append({'name':'SD Pride 2015', 'link':'/mosaic/5989', 'city':'San Diego'});
	currentArray.append({'name':'Mmm Donuts', 'link':'/mosaic/6051', 'city':'San Diego'});
	currentArray.append({'name':'Getting to know the City of Santee', 'link':'/mosaic/6062', 'city':'Santee'});
	currentArray.append({'name':'UCI Task Group 2', 'link':'/mosaic/6792', 'city':'Irvine'});
	currentArray.append({'name':'UCI 50th Anniversary', 'link':'/mosaic/6793', 'city':'Irvine'});
	currentArray.append({'name':'UCI Infinity', 'link':'/mosaic/6794', 'city':'Irvine'});
	currentArray.append({'name':'UCI Task Group 3', 'link':'/mosaic/6795', 'city':'Irvine'});
	currentArray.append({'name':'Knott s Camp Snoopy', 'link':'/mosaic/6797', 'city':'Buena Park'});
	currentArray.append({'name':'Hakone', 'link':'/mosaic/6806', 'city':'Saratoga'});
	currentArray.append({'name':'Historic Castro District', 'link':'/mosaic/6814', 'city':'San Francisco'});
	currentArray.append({'name':'Goleta Series', 'link':'/mosaic/6837', 'city':'Santa Barbara'});
	currentArray.append({'name':'Murals of Lompoc Mural Mission', 'link':'/mosaic/6987', 'city':'Lompoc'});
	currentArray.append({'name':'XM Obsessed', 'link':'/mosaic/7034', 'city':'Inglewood'});
	currentArray.append({'name':'Ballona Park', 'link':'/mosaic/7135', 'city':'Los Angeles'});
	currentArray.append({'name':'Disney Hack-the-Lot', 'link':'/mosaic/7721', 'city':'Burbank'});
	currentArray.append({'name':'CSUN Banner', 'link':'/mosaic/7722', 'city':'Los Angeles'});
	currentArray.append({'name':'Cat Collecting in Pacoima CA', 'link':'/mosaic/7876', 'city':'Los Angeles'});
	currentArray.append({'name':'Hitachi Tree', 'link':'/mosaic/9206', 'city':'Santa Clara'});
	currentArray.append({'name':'Julian Walking Tour', 'link':'/mosaic/9438', 'city':'Julian'});
	currentArray.append({'name':'Pavilion Park', 'link':'/mosaic/9821', 'city':'Irvine'});
	currentArray.append({'name':'90504', 'link':'/mosaic/9885', 'city':'Torrance'});
	currentArray.append({'name':'Resist  Jackson', 'link':'/mosaic/9886', 'city':'Jackson'});
	currentArray.append({'name':'Santana Row Mural', 'link':'/mosaic/9893', 'city':'San Jose'});
	currentArray.append({'name':'SouthBay Illuminati', 'link':'/mosaic/9895', 'city':'Carson'});
	currentArray.append({'name':'Eldorado Park', 'link':'/mosaic/10194', 'city':'Long Beach'});
	currentArray.append({'name':'Fort Humboldt at Bucksport', 'link':'/mosaic/10199', 'city':'Eureka'});
	currentArray.append({'name':'Hack Ocean Animals', 'link':'/mosaic/10391', 'city':'Sunnyvale'});
	currentArray.append({'name':'Expo Line - LA Metro', 'link':'/mosaic/10441', 'city':'Los Angeles'});
	currentArray.append({'name':'Mystic Training', 'link':'/mosaic/11104', 'city':'San Diego'});
	currentArray.append({'name':'#YOLO Around Lake Elizabeth', 'link':'/mosaic/11186', 'city':'Fremont'});
	currentArray.append({'name':'FEEL THE KERN', 'link':'/mosaic/11215', 'city':'Kernville'});
	currentArray.append({'name':'SFSU Tour', 'link':'/mosaic/11246', 'city':'San Francisco'});
	currentArray.append({'name':'Annoy the Glendale Mafia', 'link':'/mosaic/11392', 'city':'Glendale'});
	currentArray.append({'name':'Circle City Allstars', 'link':'/mosaic/11443', 'city':'Corona'});
	currentArray.append({'name':'Six Flags of Discovery Kingdom', 'link':'/mosaic/12103', 'city':'Vallejo'});
	currentArray.append({'name':'Discover Gridley', 'link':'/mosaic/12371', 'city':'Gridley'});
	currentArray.append({'name':'Naples Sunset', 'link':'/mosaic/12403', 'city':'Long Beach'});
	currentArray.append({'name':'Brace Yourself', 'link':'/mosaic/12865', 'city':'Orange'});
	currentArray.append({'name':'Sunnyvale Downtown', 'link':'/mosaic/13707', 'city':'Sunnyvale'});
	currentArray.append({'name':'La Cañada - Hack The Zip Code', 'link':'/mosaic/14306', 'city':'La Cañada Flintridge'});
	currentArray.append({'name':'90503 Zip Code', 'link':'/mosaic/14307', 'city':'Torrance'});
	currentArray.append({'name':'90505 Zip Code', 'link':'/mosaic/14308', 'city':'Torrance'});
	currentArray.append({'name':'Rainbow Cat', 'link':'/mosaic/14326', 'city':'Folsom'});
	currentArray.append({'name':'Tumbling Pandas', 'link':'/mosaic/14469', 'city':'Oakland'});
	currentArray.append({'name':'Beautiful Folsom Lake College', 'link':'/mosaic/16036', 'city':'Folsom'});
	currentArray.append({'name':'South Bay Portal Party', 'link':'/mosaic/16591', 'city':'Santa Clara'});
	currentArray.append({'name':'Rohnert Park The Friendly City', 'link':'/mosaic/16783', 'city':'Rohnert Park'});
	currentArray.append({'name':'Palo Alto Resist', 'link':'/mosaic/16904', 'city':'Palo Alto'});
	currentArray.append({'name':'MV Trees', 'link':'/mosaic/17223', 'city':'Mountain View'});
	currentArray.append({'name':'Rainbow cat parade in Old Fair Oaks', 'link':'/mosaic/17310', 'city':'Fair Oaks'});
	currentArray.append({'name':'Mascot Series', 'link':'/mosaic/17447', 'city':'Los Angeles'});
	currentArray.append({'name':'From Old to New Arroyo Grande', 'link':'/mosaic/17533', 'city':'Arroyo Grande'});
	currentArray.append({'name':'Smurfs Mission', 'link':'/mosaic/17590', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'Cool Sunnyvale Rainbow', 'link':'/mosaic/17899', 'city':'Sunnyvale'});
	currentArray.append({'name':'Lodi Resist', 'link':'/mosaic/18003', 'city':'Lodi'});
	currentArray.append({'name':'Foster City', 'link':'/mosaic/18027', 'city':'San Mateo'});
	currentArray.append({'name':'Entering Calico Ghost Town', 'link':'/mosaic/18118', 'city':'Barstow'});
	currentArray.append({'name':'Chapman Operation Blue', 'link':'/mosaic/18120', 'city':'Orange'});
	currentArray.append({'name':'Chaffey Operation Blue', 'link':'/mosaic/18121', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'Claremont Colleges Operation Blue', 'link':'/mosaic/18122', 'city':'Claremont'});
	currentArray.append({'name':'Double Lima Uniform - Operation Blue', 'link':'/mosaic/18123', 'city':'Loma Linda'});
	currentArray.append({'name':'Foxtrot Operation Blue', 'link':'/mosaic/18124', 'city':'Fontana'});
	currentArray.append({'name':'Grape Day Operation Blue', 'link':'/mosaic/18125', 'city':'Escondido'});
	currentArray.append({'name':'Ontario Operation Blue', 'link':'/mosaic/18126', 'city':'Ontario'});
	currentArray.append({'name':'Papa Sierra - Operation Blue', 'link':'/mosaic/18127', 'city':'Palm Springs'});
	currentArray.append({'name':'Pomona Operation Blue', 'link':'/mosaic/18128', 'city':'Pomona'});
	currentArray.append({'name':'Redlands Operation Blue', 'link':'/mosaic/18129', 'city':'Redlands'});
	currentArray.append({'name':'Victor Golf Operation Blue', 'link':'/mosaic/18130', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'UCD Aggies', 'link':'/mosaic/18414', 'city':'Davis'});
	currentArray.append({'name':'Presidents of Change', 'link':'/mosaic/18417', 'city':'Menlo Park'});
	currentArray.append({'name':'The Forgotten', 'link':'/mosaic/18424', 'city':'Lancaster'});
	currentArray.append({'name':'Downtown Riverbank Fun', 'link':'/mosaic/18471', 'city':'Riverbank'});
	currentArray.append({'name':'Escalon  California', 'link':'/mosaic/18558', 'city':'Escalon'});
	currentArray.append({'name':'Isla Vista series', 'link':'/mosaic/18588', 'city':'Goleta'});
	currentArray.append({'name':'Santa Clara Central Park Rainbow', 'link':'/mosaic/18599', 'city':'Santa Clara'});
	currentArray.append({'name':'Spies of Halfmoon Bay', 'link':'/mosaic/18853', 'city':'Half Moon Bay'});
	currentArray.append({'name':'IETOAD', 'link':'/mosaic/18890', 'city':'Riverside'});
	currentArray.append({'name':'Downtown Culver City', 'link':'/mosaic/19049', 'city':'Culver City'});
	currentArray.append({'name':'Capture UCI', 'link':'/mosaic/19050', 'city':'Irvine'});
	currentArray.append({'name':'Tour Santa Monica College', 'link':'/mosaic/19404', 'city':'Santa Monica'});
	currentArray.append({'name':'Secret Agent College', 'link':'/mosaic/19408', 'city':'Santa Ana'});
	currentArray.append({'name':'Chaffey Quizzes', 'link':'/mosaic/19409', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'Glyphing the College (and Gardens)', 'link':'/mosaic/19410', 'city':'Rancho Cucamonga'});
	currentArray.append({'name':'Rainbow Bridge -  420', 'link':'/mosaic/19690', 'city':'San Jose'});
	currentArray.append({'name':'Dinnertime Series', 'link':'/mosaic/20143', 'city':'Redondo Beach'});
	currentArray.append({'name':'Resist - SV', 'link':'/mosaic/20283', 'city':'Simi Valley'});
	currentArray.append({'name':'Saratoga Noble Gases', 'link':'/mosaic/20511', 'city':'Saratoga'});
	currentArray.append({'name':'Plaza de Mexico', 'link':'/mosaic/20901', 'city':'Lynwood'});
	currentArray.append({'name':'Explore Downtown Disney', 'link':'/mosaic/21054', 'city':'Anaheim'});
	currentArray.append({'name':'Sculptor  architect of XM', 'link':'/mosaic/21340', 'city':'Redlands'});
	currentArray.append({'name':'Coit Tower', 'link':'/mosaic/21380', 'city':'San Francisco'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Pasadena', 'link':'/mosaic/21908', 'city':'Pasadena'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart VV', 'link':'/mosaic/21909', 'city':'Vista'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart  Fullerton', 'link':'/mosaic/21995', 'city':'Fullerton'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart  Irvine', 'link':'/mosaic/21996', 'city':'Irvine'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart  Riverside', 'link':'/mosaic/21997', 'city':'Riverside'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart  Santa Ana', 'link':'/mosaic/22011', 'city':'Santa Ana'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart SB', 'link':'/mosaic/22150', 'city':'Solana Beach'});
	currentArray.append({'name':'Get out and Walk Pandas', 'link':'/mosaic/22166', 'city':'San Francisco'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Pasadena CalTech', 'link':'/mosaic/22175', 'city':'Pasadena'});
	currentArray.append({'name':'Red Pandas', 'link':'/mosaic/22262', 'city':'San Francisco'});
	currentArray.append({'name':'Random Pandas', 'link':'/mosaic/22263', 'city':'San Francisco'});
	currentArray.append({'name':'Resonessence Banner', 'link':'/mosaic/22431', 'city':'La Mirada'});
	currentArray.append({'name':'Mood Swing Pandas', 'link':'/mosaic/22540', 'city':'San Francisco'});
	currentArray.append({'name':'Resonnessence', 'link':'/mosaic/22639', 'city':'Los Angeles'});
	currentArray.append({'name':'Magnus Reawakens Resonessence', 'link':'/mosaic/22641', 'city':'Los Angeles'});
	currentArray.append({'name':'Carpinteria Seals', 'link':'/mosaic/23127', 'city':'Carpinteria'});
	currentArray.append({'name':'Carpinteria Pelicans', 'link':'/mosaic/23128', 'city':'Carpinteria'});
	currentArray.append({'name':'History San Jose   A Walk in the park', 'link':'/mosaic/23847', 'city':'San Jose'});
	currentArray.append({'name':'Rainbow Pandas', 'link':'/mosaic/23993', 'city':'San Francisco'});
	currentArray.append({'name':'Solar Eclipse', 'link':'/mosaic/24536', 'city':'Brea'});
	currentArray.append({'name':'Yosemite Crawl - Waterfall Series', 'link':'/mosaic/24538', 'city':'YOSEMITE NATIONAL PARK'});
	currentArray.append({'name':'You Otter See This', 'link':'/mosaic/24569', 'city':'Monterey'});
	currentArray.append({'name':'Lily Capital Smith River CA', 'link':'/mosaic/25084', 'city':'Smith River'});
	currentArray.append({'name':'Visit Crescent City California', 'link':'/mosaic/25086', 'city':'Crescent City'});
	currentArray.append({'name':'Skylawn', 'link':'/mosaic/25455', 'city':'Half Moon Bay'});
	currentArray.append({'name':'Oceanside Parks and Land Marks', 'link':'/mosaic/26126', 'city':'Oceanside'});
	currentArray.append({'name':'Celtic Series - XF Ribbon - Oceanside', 'link':'/mosaic/26257', 'city':'Oceanside'});
	currentArray.append({'name':'Aviation History at March Field', 'link':'/mosaic/26827', 'city':'March Air Reserve Base'});
	currentArray.append({'name':'San Leandro Marina', 'link':'/mosaic/27189', 'city':'San Leandro'});
	currentArray.append({'name':'rainbow fruit', 'link':'/mosaic/27909', 'city':'Concord'});

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
