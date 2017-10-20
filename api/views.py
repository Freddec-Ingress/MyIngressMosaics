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
	
	currentArray.append({'name':'Baltimore Avenue', 'link':'/mosaic/6063', 'city':' Philadelphia'});
	currentArray.append({'name':'Hop on your Bike', 'link':'/mosaic/10594', 'city':' Homestead'});
	currentArray.append({'name':'Lehigh University', 'link':'/mosaic/10872', 'city':' Bethlehem'});
	currentArray.append({'name':'Visit City Island', 'link':'/mosaic/18389', 'city':' Harrisburg'});
	currentArray.append({'name':'A Ride Along the Blue Line', 'link':'/mosaic/20850', 'city':' Philadelphia'});
	currentArray.append({'name':'Attack the WYRM', 'link':'/mosaic/20851', 'city':' Philadelphia'});
	currentArray.append({'name':'Burn Your Dread', 'link':'/mosaic/20855', 'city':' Middletown'});
	currentArray.append({'name':'DeSales University', 'link':'/mosaic/22425', 'city':' New York'});
	currentArray.append({'name':'Smurf Love', 'link':'/mosaic/23609', 'city':' Newtown'});
	currentArray.append({'name':'Philadelphia  a uniques tour', 'link':'/mosaic/9505', 'city':' Philadelphia'});
	currentArray.append({'name':'Helios Philly - Clusters', 'link':'/mosaic/19489', 'city':' Philadelphia'});
	currentArray.append({'name':'Schuylkill River Trail', 'link':'/mosaic/20221', 'city':' Philadelphia'});
	currentArray.append({'name':'Discover Saxonburg', 'link':'/mosaic/20724', 'city':' Saxonburg'});
	currentArray.append({'name':'Fifth Avenue', 'link':'/mosaic/3652', 'city':' Pittsburgh'});
	currentArray.append({'name':'First Saturday - Earn Bronze Spec Ops Badge', 'link':'/mosaic/9088', 'city':' Philadelphia'});
	currentArray.append({'name':'Connect The Dots', 'link':'/mosaic/20220', 'city':' Philadelphia'});
	currentArray.append({'name':'Greenfield Banner Art', 'link':'/mosaic/20375', 'city':' Pittsburgh'});
	currentArray.append({'name':'Coatesville Hacking', 'link':'/mosaic/20852', 'city':' Coatesville'});
	currentArray.append({'name':'Berwick Mosaic', 'link':'/mosaic/2156', 'city':' Berwick'});
	currentArray.append({'name':'Cory Mission Art', 'link':'/mosaic/2896', 'city':' Coraopolis'});
	currentArray.append({'name':'Downtown Lancaster', 'link':'/mosaic/3009', 'city':' Lancaster'});
	currentArray.append({'name':'Springton Manor', 'link':'/mosaic/4098', 'city':' Glenmoore'});
	currentArray.append({'name':'Schuylkill river', 'link':'/mosaic/4893', 'city':' Philadelphia'});
	currentArray.append({'name':'Harrisburg Skyline', 'link':'/mosaic/5002', 'city':' Harrisburg'});
	currentArray.append({'name':'UNLESS - Mission Series', 'link':'/mosaic/5888', 'city':' Harrisburg'});
	currentArray.append({'name':'Millersburg - Mission', 'link':'/mosaic/5890', 'city':' Millersburg'});
	currentArray.append({'name':'Longwood Gardens', 'link':'/mosaic/5926', 'city':' Kennett Square'});
	currentArray.append({'name':'Phoenixville', 'link':'/mosaic/5928', 'city':' Phoenixville'});
	currentArray.append({'name':'Hatboro Series', 'link':'/mosaic/5991', 'city':' Hatboro'});
	currentArray.append({'name':'Philadelphia Zoo', 'link':'/mosaic/6065', 'city':' Philadelphia'});
	currentArray.append({'name':'Franklin and Marshall', 'link':'/mosaic/6191', 'city':' Lancaster'});
	currentArray.append({'name':'Oh  the places you ll go', 'link':'/mosaic/6192', 'city':' York'});
	currentArray.append({'name':'Lewistown  Pennsylvania', 'link':'/mosaic/6193', 'city':' Lewistown'});
	currentArray.append({'name':'Explore Harborcreek', 'link':'/mosaic/8676', 'city':' Harborcreek'});
	currentArray.append({'name':'AHEC Tour of Duty', 'link':'/mosaic/8731', 'city':' Carlisle'});
	currentArray.append({'name':'Delco Tour Series Mission', 'link':'/mosaic/8926', 'city':' Media'});
	currentArray.append({'name':'Not-So-Big Bristol Badge', 'link':'/mosaic/11102', 'city':' Bristol'});
	currentArray.append({'name':'Mapping Morrisville', 'link':'/mosaic/12450', 'city':' Morrisville'});
	currentArray.append({'name':'Bradford County', 'link':'/mosaic/13464', 'city':' Sugar Run'});
	currentArray.append({'name':'Northeast Streets', 'link':'/mosaic/13653', 'city':' Philadelphia'});
	currentArray.append({'name':'Lyons Park', 'link':'/mosaic/13714', 'city':' Mertztown'});
	currentArray.append({'name':'Art of Downtown York', 'link':'/mosaic/13909', 'city':' York'});
	currentArray.append({'name':'Storming the Castle', 'link':'/mosaic/14231', 'city':' Doylestown'});
	currentArray.append({'name':'Skyline of Harrisburg  PA', 'link':'/mosaic/14673', 'city':' Harrisburg'});
	currentArray.append({'name':'Along Rt 8', 'link':'/mosaic/15078', 'city':' Erie'});
	currentArray.append({'name':'TVega$', 'link':'/mosaic/15079', 'city':' Titusville'});
	currentArray.append({'name':'Mechanicsburg Capture Mission', 'link':'/mosaic/16983', 'city':' Mechanicsburg'});
	currentArray.append({'name':'Capture Ft LeBoeuf', 'link':'/mosaic/17047', 'city':' Waterford'});
	currentArray.append({'name':'Capital City Circuit', 'link':'/mosaic/17189', 'city':' Harrisburg'});
	currentArray.append({'name':'Pottsville Brewery', 'link':'/mosaic/17309', 'city':' Pottsville'});
	currentArray.append({'name':'#MissionsForGood - Pittsburgh', 'link':'/mosaic/17530', 'city':' Pittsburgh'});
	currentArray.append({'name':'Bethlehem Steel', 'link':'/mosaic/18671', 'city':' Bethlehem'});
	currentArray.append({'name':'ROCKY', 'link':'/mosaic/18919', 'city':' York'});
	currentArray.append({'name':'Prospect Hill Cemetery', 'link':'/mosaic/18926', 'city':' York'});
	currentArray.append({'name':'Time Traveler', 'link':'/mosaic/19022', 'city':' Glenside'});
	currentArray.append({'name':'Media  PA Orange Street', 'link':'/mosaic/19612', 'city':' Media'});
	currentArray.append({'name':'Happy Trees', 'link':'/mosaic/20211', 'city':' Elysburg'});
	currentArray.append({'name':'The Bearded Geek Collective Explore York', 'link':'/mosaic/20213', 'city':' York'});
	currentArray.append({'name':'15068', 'link':'/mosaic/20726', 'city':' New Kensington'});
	currentArray.append({'name':'Love Carlisle', 'link':'/mosaic/22090', 'city':' Carlisle'});
	currentArray.append({'name':'Nazareth Speedway', 'link':'/mosaic/22203', 'city':' Nazareth'});
	currentArray.append({'name':'Wall and Piece', 'link':'/mosaic/23338', 'city':' Harrisburg'});
	currentArray.append({'name':'Philly FS December 2016', 'link':'/mosaic/24256', 'city':' Philadelphia'});
	currentArray.append({'name':'GhostBusting in Carlisle', 'link':'/mosaic/24719', 'city':' Carlisle'});
	currentArray.append({'name':'A Tour of Lititz Springs', 'link':'/mosaic/26636', 'city':' Lititz'});
	currentArray.append({'name':'Meandering past Greenfield s Sculptures', 'link':'/mosaic/26642', 'city':' Lancaster'});
	currentArray.append({'name':'Rittenhouse Square', 'link':'/mosaic/27370', 'city':' Philadelphia'});
	currentArray.append({'name':'Poconos', 'link':'/mosaic/20066', 'city':' Stroudsburg'});
	currentArray.append({'name':'Visit Pittsburgh', 'link':'/mosaic/13536', 'city':' Pittsburgh'});
	currentArray.append({'name':'Greenfield Glyph Hunt', 'link':'/mosaic/20376', 'city':' Pittsburgh'});
	currentArray.append({'name':'Wilkes-Barre Tour', 'link':'/mosaic/3632', 'city':' Wilkes-Barre'});
	currentArray.append({'name':'Willow Grove Series', 'link':'/mosaic/3668', 'city':' Willow Grove'});
	currentArray.append({'name':'ABDN-PGH', 'link':'/mosaic/8725', 'city':' Pittsburgh'});
	currentArray.append({'name':'College Tour', 'link':'/mosaic/8888', 'city':' Grove City'});
	currentArray.append({'name':'Explore Lower Frankford', 'link':'/mosaic/9065', 'city':' Philadelphia'});
	currentArray.append({'name':'Historic Philadelphia Series', 'link':'/mosaic/9201', 'city':' Philadelphia'});
	currentArray.append({'name':'Oil City Tour', 'link':'/mosaic/9662', 'city':' Oil City'});
	currentArray.append({'name':'New Hope to Lambertville', 'link':'/mosaic/9833', 'city':' New Hope'});
	currentArray.append({'name':'North East Pa mural', 'link':'/mosaic/9987', 'city':' Harborcreek'});
	currentArray.append({'name':'Knoebel s Mission Series', 'link':'/mosaic/11278', 'city':' Elysburg'});
	currentArray.append({'name':'Walking Easton', 'link':'/mosaic/12016', 'city':' Easton'});
	currentArray.append({'name':'Harrisburg Bridges', 'link':'/mosaic/12155', 'city':' Harrisburg'});
	currentArray.append({'name':'Mine Our Coal - Mission', 'link':'/mosaic/12478', 'city':' Fairview-Ferndale'});
	currentArray.append({'name':'Lovely Levittown', 'link':'/mosaic/14046', 'city':' Levittown'});
	currentArray.append({'name':'Old Harrisburg Series', 'link':'/mosaic/14097', 'city':' Harrisburg'});
	currentArray.append({'name':'NOTLD', 'link':'/mosaic/16499', 'city':' Pittsburgh'});
	currentArray.append({'name':'The Tour of the Mon Valley', 'link':'/mosaic/17096', 'city':' Monessen'});
	currentArray.append({'name':'A Tour of Franklin', 'link':'/mosaic/17429', 'city':' Franklin'});
	currentArray.append({'name':'Pottsville Tour', 'link':'/mosaic/19377', 'city':' Pottsville'});
	currentArray.append({'name':'Hersheypark Happy', 'link':'/mosaic/23375', 'city':' Hershey'});
	currentArray.append({'name':'Stuck in the Middle with You', 'link':'/mosaic/23406', 'city':' Harrisburg'});
	currentArray.append({'name':'Jersey Central Station', 'link':'/mosaic/25482', 'city':' Jim Thorpe'});
	currentArray.append({'name':'Mummers', 'link':'/mosaic/26593', 'city':' Philadelphia'});
	currentArray.append({'name':'Historic Harrisburg Series', 'link':'/mosaic/27330', 'city':' Harrisburg'});
	currentArray.append({'name':'Cousler Park', 'link':'/mosaic/20135', 'city':' York'});
	currentArray.append({'name':'MissionDay  Pittsburgh', 'link':'/mosaic/6498', 'city':' Pittsburgh'});
	currentArray.append({'name':'Philadelphia Mission Day 2017', 'link':'/mosaic/24847', 'city':' Philadelphia'});
	currentArray.append({'name':'Harrisburg Capitol Series', 'link':'/mosaic/3405', 'city':' Harrisburg'});
	currentArray.append({'name':'The Golden Triangle', 'link':'/mosaic/5141', 'city':' Pittsburgh'});
	currentArray.append({'name':'Erie Bicentennial Tower', 'link':'/mosaic/5930', 'city':' Erie'});
	currentArray.append({'name':'We Have Met The Enemy  and they are Ours', 'link':'/mosaic/6374', 'city':' Erie'});
	currentArray.append({'name':'Avenue of the Arts', 'link':'/mosaic/6639', 'city':' Philadelphia'});
	currentArray.append({'name':'Calvary Cemetery Banner Art', 'link':'/mosaic/7860', 'city':' Pittsburgh'});
	currentArray.append({'name':'Center City Skyline', 'link':'/mosaic/7884', 'city':' Philadelphia'});
	currentArray.append({'name':'McPherson Ridge - Gettysburg', 'link':'/mosaic/8227', 'city':' Gettysburg'});
	currentArray.append({'name':'Visit Downtown York PA', 'link':'/mosaic/8556', 'city':' York'});
	currentArray.append({'name':'Allentown-Downtown', 'link':'/mosaic/8739', 'city':' Allentown'});
	currentArray.append({'name':'Media Banner Series', 'link':'/mosaic/9301', 'city':' Media'});
	currentArray.append({'name':'Swarthmore Banner Series', 'link':'/mosaic/9322', 'city':' Swarthmore'});
	currentArray.append({'name':'Bella Vista -  Beautiful Sight', 'link':'/mosaic/9581', 'city':' Philadelphia'});
	currentArray.append({'name':'Pagoda Panoramic Parade', 'link':'/mosaic/11348', 'city':' Reading'});
	currentArray.append({'name':'Ursinus College (A Bear of a School)', 'link':'/mosaic/11913', 'city':' Collegeville'});
	currentArray.append({'name':'Natural Freedoms', 'link':'/mosaic/11914', 'city':' Phoenixville'});
	currentArray.append({'name':'Longwood - Italian Water Garden', 'link':'/mosaic/12627', 'city':' Kennett Square'});
	currentArray.append({'name':'Lehigh University Mosaic', 'link':'/mosaic/12681', 'city':' Bethlehem'});
	currentArray.append({'name':'Explore the Slate Belt region', 'link':'/mosaic/13448', 'city':' Wind Gap'});
	currentArray.append({'name':'Dragon', 'link':'/mosaic/14664', 'city':' York'});
	currentArray.append({'name':'Harrisburg Map', 'link':'/mosaic/14902', 'city':' Harrisburg'});
	currentArray.append({'name':'ENL Cheeky Tree Frog', 'link':'/mosaic/15150', 'city':' Pittsburgh'});
	currentArray.append({'name':'I  lt 3 York  PA', 'link':'/mosaic/16260', 'city':' York'});
	currentArray.append({'name':'West Chester Banner', 'link':'/mosaic/17163', 'city':' West Chester'});
	currentArray.append({'name':'Explore Downtown Pittsburgh', 'link':'/mosaic/17862', 'city':' Pittsburgh'});
	currentArray.append({'name':'Gnome Exploration', 'link':'/mosaic/18179', 'city':' Bristol'});
	currentArray.append({'name':'Welcome to Bluetown', 'link':'/mosaic/18547', 'city':' Newtown'});
	currentArray.append({'name':'Join the Resistance', 'link':'/mosaic/19772', 'city':' Ambler'});
	currentArray.append({'name':'Yinzgress Mission Day', 'link':'/mosaic/21005', 'city':' Pittsburgh'});
	currentArray.append({'name':'Newtown Smurfcrusher', 'link':'/mosaic/21564', 'city':' Newtown'});
	currentArray.append({'name':'Chuck Norristown', 'link':'/mosaic/21895', 'city':' Norristown'});
	currentArray.append({'name':'To Boldly Go - Pottstown', 'link':'/mosaic/22462', 'city':' Pottstown'});
	currentArray.append({'name':'Dansbury Depot', 'link':'/mosaic/23228', 'city':' Stroudsburg'});
	currentArray.append({'name':'Cousler Park Wizardry', 'link':'/mosaic/23443', 'city':' York'});
	currentArray.append({'name':'WC Parks Banner', 'link':'/mosaic/23487', 'city':' West Chester'});
	currentArray.append({'name':'Dial the Gate', 'link':'/mosaic/23661', 'city':' Conshohocken'});
	currentArray.append({'name':'And There Was Much Rejoicing', 'link':'/mosaic/23760', 'city':' Philadelphia'});
	currentArray.append({'name':'Mercer County Driving Tour', 'link':'/mosaic/25571', 'city':' West Middlesex'});
	currentArray.append({'name':'Taking Out the Trash', 'link':'/mosaic/25598', 'city':' Middletown'});
	currentArray.append({'name':'Capital Greenbelt Riverview', 'link':'/mosaic/25797', 'city':' Harrisburg'});
	currentArray.append({'name':'A Tour of Lancaster', 'link':'/mosaic/26654', 'city':' Lancaster'});
	currentArray.append({'name':'BattleToads', 'link':'/mosaic/27186', 'city':' Lancaster'});
	currentArray.append({'name':'The Great Wave', 'link':'/mosaic/27331', 'city':' Harrisburg'});
	currentArray.append({'name':'Capitol appreciation', 'link':'/mosaic/27527', 'city':' Harrisburg'});
	currentArray.append({'name':'Philadelphia - UPENN', 'link':'/mosaic/4892', 'city':' Philadelphia'});
	currentArray.append({'name':'Philadelphia - Art Museum', 'link':'/mosaic/4895', 'city':' Philadelphia'});
	currentArray.append({'name':'Ben Franklin Bridge', 'link':'/mosaic/5611', 'city':' Philadelphia'});
	currentArray.append({'name':'Take control of York', 'link':'/mosaic/5924', 'city':' York'});
	currentArray.append({'name':'Lost Mural of Phoenixville', 'link':'/mosaic/5927', 'city':' Phoenixville'});
	currentArray.append({'name':'Bethlehem-Downtown', 'link':'/mosaic/7499', 'city':' Bethlehem'});
	currentArray.append({'name':'Longwood Gardens Mission Series', 'link':'/mosaic/8655', 'city':' Kennett Square'});
	currentArray.append({'name':'Hogwarts of Hanover', 'link':'/mosaic/9210', 'city':' Hanover'});
	currentArray.append({'name':'Olde City Philly', 'link':'/mosaic/10240', 'city':' Philadelphia'});
	currentArray.append({'name':'Hacking gear around York', 'link':'/mosaic/14057', 'city':' York'});
	currentArray.append({'name':'Chinatown Friendship Gate', 'link':'/mosaic/15774', 'city':' Philadelphia'});
	currentArray.append({'name':'Valley Forge', 'link':'/mosaic/15937', 'city':' Wayne'});
	currentArray.append({'name':'Greetings', 'link':'/mosaic/17985', 'city':' Philadelphia'});
	currentArray.append({'name':'Carlisle Square', 'link':'/mosaic/21869', 'city':' Carlisle'});
	currentArray.append({'name':'Philadelphia - City Hall', 'link':'/mosaic/4894', 'city':' Philadelphia'});
	currentArray.append({'name':'Bird Dog', 'link':'/mosaic/27310', 'city':' Philadelphia'});
	currentArray.append({'name':'Cathedral of Learning', 'link':'/mosaic/7880', 'city':' Pittsburgh'});
	currentArray.append({'name':'Philadelphia - Liberty Bell', 'link':'/mosaic/9256', 'city':' Philadelphia'});
	currentArray.append({'name':'Ant Carver', 'link':'/mosaic/15692', 'city':' Philadelphia'});
	currentArray.append({'name':'Conquer It All', 'link':'/mosaic/5467', 'city':' York'});

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
