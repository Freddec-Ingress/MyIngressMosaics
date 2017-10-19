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

	currentArray.append({'name':'I Love The Bronx Mural', 'link':'/mosaic/3651', 'city':'New York'});
	currentArray.append({'name':'World Trade Center Tour', 'link':'/mosaic/3665', 'city':'New York'});
	currentArray.append({'name':'Ingress Items 2', 'link':'/mosaic/3703', 'city':'New York'});
	currentArray.append({'name':'Hudson', 'link':'/mosaic/4901', 'city':'Hudson'});
	currentArray.append({'name':'Islip Town', 'link':'/mosaic/5910', 'city':'Islip'});
	currentArray.append({'name':'Buffalo Bills Fan Mission', 'link':'/mosaic/8870', 'city':'Orchard Park'});
	currentArray.append({'name':'Spot the Ewes', 'link':'/mosaic/9905', 'city':'New York'});
	currentArray.append({'name':'Just Invader Cutie Pandas', 'link':'/mosaic/10640', 'city':'New York'});
	currentArray.append({'name':'NYC Represent RES', 'link':'/mosaic/11510', 'city':'New York'});
	currentArray.append({'name':'Cazenovia', 'link':'/mosaic/11606', 'city':'Cazenovia'});
	currentArray.append({'name':'Avenue P', 'link':'/mosaic/12121', 'city':'New York'});
	currentArray.append({'name':'Give Me Liberty  or Give Me Victory', 'link':'/mosaic/12647', 'city':'New York'});
	currentArray.append({'name':'OBP Boardwalk Banner Mission', 'link':'/mosaic/13178', 'city':'Rochester'});
	currentArray.append({'name':'Ingress First Saturday - Beacon NY', 'link':'/mosaic/13450', 'city':'Beacon'});
	currentArray.append({'name':'Canadaigua City Pier Banner', 'link':'/mosaic/13745', 'city':'Canandaigua'});
	currentArray.append({'name':'Churches of the towns of Western New York', 'link':'/mosaic/13748', 'city':'Western New York'});
	currentArray.append({'name':'Historic LeRoy Banner For IngressFS', 'link':'/mosaic/16580', 'city':'Le Roy'});
	currentArray.append({'name':'A High Falls IngressFS Banner', 'link':'/mosaic/16778', 'city':'Rochester'});
	currentArray.append({'name':'Rochester IngressFS Banner in Newark', 'link':'/mosaic/17684', 'city':'Newark'});
	currentArray.append({'name':'Sneaky Frogs Build a Farm', 'link':'/mosaic/17920', 'city':'Rochester (and surrounding)'});
	currentArray.append({'name':'Geneseo Banner #IngressFS', 'link':'/mosaic/18183', 'city':'Geneseo'});
	currentArray.append({'name':'IngressFS South Wedge Banner', 'link':'/mosaic/18655', 'city':'Rochester'});
	currentArray.append({'name':'Fatima Capture', 'link':'/mosaic/18960', 'city':'Youngstown'});
	currentArray.append({'name':'Bridges of NYC', 'link':'/mosaic/18968', 'city':'New York'});
	currentArray.append({'name':'5k Series', 'link':'/mosaic/20160', 'city':'Johnson City'});
	currentArray.append({'name':'Saints in Brooklyn', 'link':'/mosaic/22094', 'city':'New York'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart - New York State  Colored Hearts', 'link':'/mosaic/22361', 'city':'Albany, Syracuse, Binghamton, Ithaca, Rochester, Buffalo'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart  SS NY', 'link':'/mosaic/22380', 'city':'Saratoga Springs'});
	currentArray.append({'name':'Children s Missions of Mamaroneck', 'link':'/mosaic/22756', 'city':'Mamaroneck'});
	currentArray.append({'name':'Subway Mission', 'link':'/mosaic/23276', 'city':'Rochester'});
	currentArray.append({'name':'Lefrak', 'link':'/mosaic/23311', 'city':'New York'});
	currentArray.append({'name':'Just Invader Sleepy Pandas', 'link':'/mosaic/24142', 'city':'New York'});
	currentArray.append({'name':'Rochester Pride Parade 2017', 'link':'/mosaic/24433', 'city':'Rochester'});
	currentArray.append({'name':'Dizzy Daze', 'link':'/mosaic/24713', 'city':'Albany'});
	currentArray.append({'name':'Buffalo Pride Mission Banner', 'link':'/mosaic/24922', 'city':'Buffalo'});
	currentArray.append({'name':'Buffalo Olmstead Parks One Row Mission Banner', 'link':'/mosaic/25182', 'city':'Buffalo'});
	currentArray.append({'name':'Buffalo Theater District', 'link':'/mosaic/25414', 'city':'Buffalo'});
	currentArray.append({'name':'Lasdon Park', 'link':'/mosaic/25434', 'city':'Katonah'});
	currentArray.append({'name':'Making Music', 'link':'/mosaic/25440', 'city':'Albany'});
	currentArray.append({'name':'John Jay Homestead', 'link':'/mosaic/25834', 'city':'Katonah'});
	currentArray.append({'name':'Highway to Heaven', 'link':'/mosaic/25989', 'city':'Buffalo'});
	currentArray.append({'name':'Chuang Yen Monastery', 'link':'/mosaic/26315', 'city':'Carmel Hamlet'});
	currentArray.append({'name':'Explore Geneseo', 'link':'/mosaic/26577', 'city':'Geneseo'});
	currentArray.append({'name':'The Cooper Union Tour', 'link':'/mosaic/26689', 'city':'New York'});
	currentArray.append({'name':'#IngressFS October Rochester NY', 'link':'/mosaic/26797', 'city':'Fairport'});
	currentArray.append({'name':'#IngressFS September 2017 Rochester NY', 'link':'/mosaic/26798', 'city':'Geneva'});
	currentArray.append({'name':'Shelter Island  New York', 'link':'/mosaic/27400', 'city':'Shelter Island Heights'});
	currentArray.append({'name':'Monorail  Monorail  Monorail', 'link':'/mosaic/27541', 'city':'Rochester'});
	currentArray.append({'name':'Use the Force  - Saratoga Springs NY', 'link':'/mosaic/27913', 'city':'Saratoga Springs'});
	currentArray.append({'name':'Elmhurst Religious Institutions', 'link':'/mosaic/3688', 'city':'New York'});
	currentArray.append({'name':'BMTS - Seven Bike Routes', 'link':'/mosaic/19915', 'city':'Kirkwood'});
	currentArray.append({'name':'Peekskill', 'link':'/mosaic/16987', 'city':'Cortlandt'});
	currentArray.append({'name':'Blocks in New York', 'link':'/mosaic/18949', 'city':'Rochester'});
	currentArray.append({'name':'UB North Hacks', 'link':'/mosaic/20398', 'city':'Buffalo'});
	currentArray.append({'name':'Ingress Items 1', 'link':'/mosaic/3701', 'city':'New York'});
	currentArray.append({'name':'Financial District March', 'link':'/mosaic/1963', 'city':'New York'});
	currentArray.append({'name':'NYC Skyline', 'link':'/mosaic/1965', 'city':'New York'});
	currentArray.append({'name':'Barclay Center', 'link':'/mosaic/1985', 'city':'New York'});
	currentArray.append({'name':'Verrazano Bridge Views', 'link':'/mosaic/2119', 'city':'New York'});
	currentArray.append({'name':'Greetings from Red Hook', 'link':'/mosaic/2123', 'city':'New York'});
	currentArray.append({'name':'Hell Gate Bridge Series', 'link':'/mosaic/2949', 'city':'New York'});
	currentArray.append({'name':'Chinese New Year Parade Route 2015', 'link':'/mosaic/3640', 'city':'New York'});
	currentArray.append({'name':'West Village Zodiac', 'link':'/mosaic/3641', 'city':'New York'});
	currentArray.append({'name':'12 Chinese Zodiac Animals', 'link':'/mosaic/3644', 'city':'New York'});
	currentArray.append({'name':'Celestial Bodies', 'link':'/mosaic/3653', 'city':'New York'});
	currentArray.append({'name':'Shaker Heritage', 'link':'/mosaic/5651', 'city':'Albany'});
	currentArray.append({'name':'El Barrio Eats', 'link':'/mosaic/6486', 'city':'New York'});
	currentArray.append({'name':'How to be a panda in the West Village', 'link':'/mosaic/7035', 'city':'New York'});
	currentArray.append({'name':'Endless Optimism in Buffalo', 'link':'/mosaic/8692', 'city':'Orchard Park'});
	currentArray.append({'name':'INGRESS FIRST SATURDAY - BEACON  NY', 'link':'/mosaic/15385', 'city':'Beacon'});
	currentArray.append({'name':'Welcome to Flushing  Queens', 'link':'/mosaic/18046', 'city':'New York'});
	currentArray.append({'name':'Months Missions - Vestal  NY', 'link':'/mosaic/19876', 'city':'Vestal'});
	currentArray.append({'name':'Thoroughbreds', 'link':'/mosaic/23735', 'city':'Saratoga Springs'});
	currentArray.append({'name':'NFTA Metro Rail Mission Banner', 'link':'/mosaic/25278', 'city':'Buffalo'});
	currentArray.append({'name':'Shark Girl Walking Mission', 'link':'/mosaic/25497', 'city':'Buffalo'});
	currentArray.append({'name':'Chuck Wood', 'link':'/mosaic/26129', 'city':'Albany'});
	currentArray.append({'name':'All Along the Buffalo Waterfront', 'link':'/mosaic/26466', 'city':'Buffalo'});
	currentArray.append({'name':'Explorer Series - Binghamton', 'link':'/mosaic/20161', 'city':'Binghamton'});
	currentArray.append({'name':'Susan B  Anthony  Independence is Happiness', 'link':'/mosaic/23853', 'city':'Rochester'});
	currentArray.append({'name':'Plattsburgh', 'link':'/mosaic/369', 'city':'Plattsburgh'});
	currentArray.append({'name':'Sights Of St  George Part', 'link':'/mosaic/1551', 'city':'New York'});
	currentArray.append({'name':'Manhattan Bridge', 'link':'/mosaic/1961', 'city':'New York'});
	currentArray.append({'name':'George Washington Bridge', 'link':'/mosaic/1988', 'city':'New York'});
	currentArray.append({'name':'Sunset Park', 'link':'/mosaic/1990', 'city':'New York'});
	currentArray.append({'name':'Green-Wood Cemetery', 'link':'/mosaic/2120', 'city':'New York'});
	currentArray.append({'name':'Oceanside History Series', 'link':'/mosaic/3347', 'city':'Island Park'});
	currentArray.append({'name':'South Shore of Long Island', 'link':'/mosaic/3348', 'city':'Babylon'});
	currentArray.append({'name':'7 Train Stations', 'link':'/mosaic/3700', 'city':'New York'});
	currentArray.append({'name':'Greetings From Coney Island', 'link':'/mosaic/6958', 'city':'New York'});
	currentArray.append({'name':'Columbia University', 'link':'/mosaic/7937', 'city':'New York'});
	currentArray.append({'name':'RPI Engineering Tour', 'link':'/mosaic/8993', 'city':'Troy'});
	currentArray.append({'name':'5Boro Bike Tour', 'link':'/mosaic/9574', 'city':'New York'});
	currentArray.append({'name':'Flushing Meadows–Corona Park', 'link':'/mosaic/9585', 'city':'New York'});
	currentArray.append({'name':'Ozymandias of Downtown Brooklyn', 'link':'/mosaic/10363', 'city':'New York'});
	currentArray.append({'name':'Aegis Nova Brooklyn', 'link':'/mosaic/10525', 'city':'New York'});
	currentArray.append({'name':'Greetings From The Bronx', 'link':'/mosaic/11519', 'city':'New York'});
	currentArray.append({'name':'Downtown Syracuse', 'link':'/mosaic/11655', 'city':'Syracuse'});
	currentArray.append({'name':'Saratoga Murals - Congress Park', 'link':'/mosaic/11675', 'city':'Saratoga Springs'});
	currentArray.append({'name':'Eyes of the Enlightened', 'link':'/mosaic/11879', 'city':'New York'});
	currentArray.append({'name':'Rizzi', 'link':'/mosaic/12093', 'city':'New York'});
	currentArray.append({'name':'Postcards From Bensonhurst', 'link':'/mosaic/12350', 'city':'New York'});
	currentArray.append({'name':'Leonid Afremov s Oil Painting @UB', 'link':'/mosaic/14186', 'city':'Buffalo'});
	currentArray.append({'name':'Proud Otter', 'link':'/mosaic/14456', 'city':'New York'});
	currentArray.append({'name':'Circle of Life - Bear and Salmon', 'link':'/mosaic/14457', 'city':'New York'});
	currentArray.append({'name':'Niagara Falls USA', 'link':'/mosaic/14723', 'city':'Niagara Falls'});
	currentArray.append({'name':'Rochester Celebrations', 'link':'/mosaic/16764', 'city':'Rochester'});
	currentArray.append({'name':'Washington Square Park NYU Tour', 'link':'/mosaic/16794', 'city':'New York'});
	currentArray.append({'name':'Frontier Trekker   1 18', 'link':'/mosaic/18148', 'city':'Youngstown'});
	currentArray.append({'name':'Hometown Owego', 'link':'/mosaic/19250', 'city':'Owego'});
	currentArray.append({'name':'The Lion of Irondequoit', 'link':'/mosaic/19888', 'city':'Rochester'});
	currentArray.append({'name':'The Polar Bear of Perinton', 'link':'/mosaic/19889', 'city':'Perinton (Fairport)'});
	currentArray.append({'name':'ROCQUEERGRESS', 'link':'/mosaic/19891', 'city':'Rochester'});
	currentArray.append({'name':'The Wolf of Webster', 'link':'/mosaic/20391', 'city':'Webster'});
	currentArray.append({'name':'The Tiger of Charlotte', 'link':'/mosaic/21779', 'city':'Rochester'});
	currentArray.append({'name':'Magnus Reawakens - Luminescent Heart - New York State', 'link':'/mosaic/21926', 'city':'Waterloo'});
	currentArray.append({'name':'Twilight Zone', 'link':'/mosaic/22895', 'city':'Binghamton'});
	currentArray.append({'name':'Birthplace of the Women s Rights Movement', 'link':'/mosaic/23412', 'city':'Rochester'});
	currentArray.append({'name':'The Metropolitan', 'link':'/mosaic/23852', 'city':'Rochester'});
	currentArray.append({'name':'Rochester s Public Market', 'link':'/mosaic/23855', 'city':'Rochester'});
	currentArray.append({'name':'LGBTQ+ Pride', 'link':'/mosaic/24032', 'city':'Rochester'});
	currentArray.append({'name':'Grand Army Plaza', 'link':'/mosaic/24242', 'city':'Brooklyn'});
	currentArray.append({'name':'The Crow s Eye', 'link':'/mosaic/24438', 'city':'New York'});
	currentArray.append({'name':'Vega-Nor  Lockport  NY Hacking Mission', 'link':'/mosaic/25183', 'city':'Lockport'});
	currentArray.append({'name':'Ebbets Field', 'link':'/mosaic/25537', 'city':'New York'});
	currentArray.append({'name':'I Need A Fast Car', 'link':'/mosaic/25552', 'city':'Albany'});
	currentArray.append({'name':'Rainey Memorial Gates', 'link':'/mosaic/25584', 'city':'New York'});
	currentArray.append({'name':'SUNY Geneseo', 'link':'/mosaic/25595', 'city':'Geneseo'});
	currentArray.append({'name':'UB Zombies', 'link':'/mosaic/25610', 'city':'Buffalo'});
	currentArray.append({'name':'Blues Brothers', 'link':'/mosaic/25759', 'city':'New York'});
	currentArray.append({'name':'The Nickel City', 'link':'/mosaic/26468', 'city':'Buffalo'});
	currentArray.append({'name':'Visit Storm King Art Center', 'link':'/mosaic/27712', 'city':'New Windsor'});
	currentArray.append({'name':'Lost in Yonkers', 'link':'/mosaic/27714', 'city':'Yonkers'});
	currentArray.append({'name':'MissionDay Albany', 'link':'/mosaic/4346', 'city':'Albany'});
	currentArray.append({'name':'DUMBO', 'link':'/mosaic/1960', 'city':'New York'});
	currentArray.append({'name':'Brooklyn Bridge', 'link':'/mosaic/1962', 'city':'New York'});
	currentArray.append({'name':'Stars Over Woodlawn', 'link':'/mosaic/1984', 'city':'New York'});
	currentArray.append({'name':'Renaissance Era', 'link':'/mosaic/1989', 'city':'New York'});
	currentArray.append({'name':'Long Beach History Series', 'link':'/mosaic/3346', 'city':'Long Beach'});
	currentArray.append({'name':'Central Park in the Rain', 'link':'/mosaic/3638', 'city':'New York'});
	currentArray.append({'name':'Central Park', 'link':'/mosaic/3639', 'city':'New York'});
	currentArray.append({'name':'State Island Ferry MIssion', 'link':'/mosaic/3695', 'city':'New York'});
	currentArray.append({'name':'The Brooklyn Riviera', 'link':'/mosaic/3696', 'city':'New York'});
	currentArray.append({'name':'Bear Mountain Bridge', 'link':'/mosaic/4074', 'city':'Tomkins Cove'});
	currentArray.append({'name':'Greetings From Long Island', 'link':'/mosaic/4257', 'city':'Babylon'});
	currentArray.append({'name':'Coney Island Avenue', 'link':'/mosaic/6959', 'city':'New York'});
	currentArray.append({'name':'Empire State Building (Panda Edition)', 'link':'/mosaic/7814', 'city':'New York'});
	currentArray.append({'name':'Albany - District 1', 'link':'/mosaic/8647', 'city':'Albany'});
	currentArray.append({'name':'Inside Chautauqua Institution', 'link':'/mosaic/9277', 'city':'Mayville'});
	currentArray.append({'name':'WTC Memorial', 'link':'/mosaic/9558', 'city':'New York'});
	currentArray.append({'name':'Avengers Tower', 'link':'/mosaic/10772', 'city':'New York'});
	currentArray.append({'name':'Midtown Skyline NYC', 'link':'/mosaic/17851', 'city':'New York'});
	currentArray.append({'name':'Valhalla', 'link':'/mosaic/24439', 'city':'New York'});
	currentArray.append({'name':'Headless Horseman', 'link':'/mosaic/13934', 'city':'Sleepy Hollow'});
	currentArray.append({'name':'Big Apple', 'link':'/mosaic/1964', 'city':'New York'});
	currentArray.append({'name':'Buffalo Dyngus Day', 'link':'/mosaic/8871', 'city':'Buffalo'});
	currentArray.append({'name':'Who you gonna call', 'link':'/mosaic/9401', 'city':'New York'});
	currentArray.append({'name':'Bike NYC', 'link':'/mosaic/16930', 'city':'New York'});
	currentArray.append({'name':'Capital District Tour', 'link':'/mosaic/23117', 'city':'Troy'});
	currentArray.append({'name':'MissionDay Brooklyn', 'link':'/mosaic/10737', 'city':'New York'});
	currentArray.append({'name':'Just Invader With A Parasol', 'link':'/mosaic/1966', 'city':'New York'});
	currentArray.append({'name':'The God of Thunder', 'link':'/mosaic/24766', 'city':'New York'});
	currentArray.append({'name':'Montauk  The End', 'link':'/mosaic/5652', 'city':'Bay Shore'});
	currentArray.append({'name':'Woodlawn Cemetery', 'link':'/mosaic/1967', 'city':'New York'});
	currentArray.append({'name':'Statue of Liberty', 'link':'/mosaic/27879', 'city':'New York'});

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
