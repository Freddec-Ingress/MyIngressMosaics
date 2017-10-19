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
	
	currentArray.append({'name':'Donuts - Minnehaha Park', 'link':'/mosaic/21386', 'city':'Minneapolis'});
	currentArray.append({'name':'April Fools IngressFS', 'link':'/mosaic/21818', 'city':'Excelsior'});
	currentArray.append({'name':'Cities MN', 'link':'/mosaic/22514', 'city':'Chisholm'});
	currentArray.append({'name':'University of M___', 'link':'/mosaic/23744', 'city':'Minneapolis'});
	currentArray.append({'name':'#IngressFS July Twin Cities', 'link':'/mosaic/24782', 'city':'Saint Paul'});
	currentArray.append({'name':'#IngressFS October Twin Cities', 'link':'/mosaic/27898', 'city':'Minneapolis'});
	currentArray.append({'name':'Big Ole', 'link':'/mosaic/19867', 'city':'Alexandria'});
	currentArray.append({'name':'Welcome to Alexandria', 'link':'/mosaic/20041', 'city':'Alexandria'});
	currentArray.append({'name':'Shakopee Parks', 'link':'/mosaic/20506', 'city':'Shakopee'});
	currentArray.append({'name':'Smurf Hydrant', 'link':'/mosaic/23088', 'city':'Rosemount'});
	currentArray.append({'name':'College of St Bens', 'link':'/mosaic/7929', 'city':'Saint Joseph'});
	currentArray.append({'name':'Tribute to Niantic', 'link':'/mosaic/8628', 'city':'Minneapolis'});
	currentArray.append({'name':'Sartell St  Stephen Sabers', 'link':'/mosaic/9007', 'city':'Saint Stephen'});
	currentArray.append({'name':'LinkBall at Todd', 'link':'/mosaic/4392', 'city':'Austin'});
	currentArray.append({'name':'CLP Zodiac', 'link':'/mosaic/3305', 'city':'Minneapolis'});
	currentArray.append({'name':'The War of Shapers', 'link':'/mosaic/3307', 'city':'Minneapolis'});
	currentArray.append({'name':'Mystery Science Mission 3000', 'link':'/mosaic/3316', 'city':'Minneapolis'});
	currentArray.append({'name':'Victory Memorial Drive', 'link':'/mosaic/3321', 'city':'Minneapolis'});
	currentArray.append({'name':'Sartell', 'link':'/mosaic/3323', 'city':'Sartell'});
	currentArray.append({'name':'Full Moon Mural', 'link':'/mosaic/3326', 'city':'Duluth'});
	currentArray.append({'name':'Runes', 'link':'/mosaic/3870', 'city':'Champlin'});
	currentArray.append({'name':'Western Zodiac', 'link':'/mosaic/5974', 'city':'Minneapolis'});
	currentArray.append({'name':'Eden Prairie Mallrats', 'link':'/mosaic/7777', 'city':'Eden Prairie'});
	currentArray.append({'name':'Rochester Skyline Mural', 'link':'/mosaic/7779', 'city':'Rochester'});
	currentArray.append({'name':'Saint Anthony Falls Bridge Tour', 'link':'/mosaic/9638', 'city':'Minneapolis'});
	currentArray.append({'name':'Watertown  Minnesota - Cottage Hospital', 'link':'/mosaic/9639', 'city':'Watertown'});
	currentArray.append({'name':'Mille Lacs Circle Tour', 'link':'/mosaic/9661', 'city':'Aitkin'});
	currentArray.append({'name':'That Dam Banner', 'link':'/mosaic/9667', 'city':'Saint Cloud'});
	currentArray.append({'name':'Parks of Brooklyn Park', 'link':'/mosaic/10149', 'city':'Minneapolis'});
	currentArray.append({'name':'Lake Street Adventure', 'link':'/mosaic/11268', 'city':'Minneapolis'});
	currentArray.append({'name':'Mankato Downtown', 'link':'/mosaic/12147', 'city':'Mankato'});
	currentArray.append({'name':'St Kate s (Colleges of St Paul)', 'link':'/mosaic/12173', 'city':'Saint Paul'});
	currentArray.append({'name':'Red Wing  Minnesota', 'link':'/mosaic/12651', 'city':'Red Wing'});
	currentArray.append({'name':'Tribute to Tilt-A-Whirl', 'link':'/mosaic/12652', 'city':'Faribault'});
	currentArray.append({'name':'Marshall Mosaic', 'link':'/mosaic/14064', 'city':'Marshall'});
	currentArray.append({'name':'No Greater Love', 'link':'/mosaic/16109', 'city':'Saint Paul'});
	currentArray.append({'name':'Zombie Outbreak Response Team', 'link':'/mosaic/16264', 'city':'Minneapolis'});
	currentArray.append({'name':'Rochester City Parks', 'link':'/mosaic/17101', 'city':'Rochester'});
	currentArray.append({'name':'Orange You Happy You are in Lakeville', 'link':'/mosaic/17253', 'city':'Burnsville'});
	currentArray.append({'name':'Lakewalk banner', 'link':'/mosaic/17863', 'city':'Duluth'});
	currentArray.append({'name':'First In  Last Out', 'link':'/mosaic/17912', 'city':'Saint Paul'});
	currentArray.append({'name':'To Protect and Serve', 'link':'/mosaic/17913', 'city':'Saint Paul'});
	currentArray.append({'name':'North Saint Paul', 'link':'/mosaic/19378', 'city':'Saint Paul'});
	currentArray.append({'name':'Magic', 'link':'/mosaic/20823', 'city':'Lakeville'});
	currentArray.append({'name':'2016 Minnesota Twins', 'link':'/mosaic/21461', 'city':'Minneapolis'});
	currentArray.append({'name':'Aitkin Banner', 'link':'/mosaic/23101', 'city':'Aitkin'});
	currentArray.append({'name':'Operation Teal Ribbon', 'link':'/mosaic/23349', 'city':'Minneapolis'});
	currentArray.append({'name':'The Bluest Blue Ever', 'link':'/mosaic/23407', 'city':'Saint Paul'});
	currentArray.append({'name':'County Hwy 61', 'link':'/mosaic/25177', 'city':'Barnum'});
	currentArray.append({'name':'Minneapolis Rex', 'link':'/mosaic/25178', 'city':'Minneapolis'});
	currentArray.append({'name':'I ll Show You The Darkside', 'link':'/mosaic/25468', 'city':'Saint Paul'});
	currentArray.append({'name':'Enlightened Angel', 'link':'/mosaic/23091', 'city':'Rosemount'});
	currentArray.append({'name':'State Quarters - Explore the US', 'link':'/mosaic/661', 'city':'Minneapolis'});
	currentArray.append({'name':'Cows  Colleges Contentment', 'link':'/mosaic/3294', 'city':'Northfield'});
	currentArray.append({'name':'Follow The Butterflies at the MN Arboretum', 'link':'/mosaic/3304', 'city':'Excelsior'});
	currentArray.append({'name':'Exploring Harriet', 'link':'/mosaic/3309', 'city':'Minneapolis'});
	currentArray.append({'name':'Exploring Minneapolis', 'link':'/mosaic/3310', 'city':'Minneapolis'});
	currentArray.append({'name':'Discovering UMN', 'link':'/mosaic/3318', 'city':'Minneapolis'});
	currentArray.append({'name':'Skyline Parkway - Kitchi Gammi Park', 'link':'/mosaic/3324', 'city':'Duluth'});
	currentArray.append({'name':'New Ulm  Minnesota', 'link':'/mosaic/5671', 'city':'New Ulm'});
	currentArray.append({'name':'The Cat s Meow', 'link':'/mosaic/5934', 'city':'Saint Paul'});
	currentArray.append({'name':'Explore Downtown Stillwater', 'link':'/mosaic/6646', 'city':'Stillwater'});
	currentArray.append({'name':'Maple Grove Mosaic', 'link':'/mosaic/7705', 'city':'Osseo'});
	currentArray.append({'name':'Northeast Squirrel Canoe', 'link':'/mosaic/7781', 'city':'Minneapolis'});
	currentArray.append({'name':'2016 Stadium Series', 'link':'/mosaic/7783', 'city':'Minneapolis'});
	currentArray.append({'name':'a Corn Fields - Savage Minnesota', 'link':'/mosaic/7784', 'city':'Savage'});
	currentArray.append({'name':'Albert Lea Minnesota', 'link':'/mosaic/7785', 'city':'Albert Lea'});
	currentArray.append({'name':'Hutchinson Minnesota', 'link':'/mosaic/7786', 'city':'Hutchinson'});
	currentArray.append({'name':'Outdoor Hockey Mural', 'link':'/mosaic/7787', 'city':'Minneapolis'});
	currentArray.append({'name':'Military Cemetery Banner', 'link':'/mosaic/8528', 'city':'Little Falls'});
	currentArray.append({'name':'Warrior s Choice - Camp Ripley', 'link':'/mosaic/8529', 'city':'Little Falls'});
	currentArray.append({'name':'West Metro In A Pickle', 'link':'/mosaic/8711', 'city':'Chaska'});
	currentArray.append({'name':'Apple Core', 'link':'/mosaic/9561', 'city':'Saint Paul'});
	currentArray.append({'name':'Above the Falls', 'link':'/mosaic/9565', 'city':'Minneapolis'});
	currentArray.append({'name':'Wizard of Oz', 'link':'/mosaic/9566', 'city':'Grand Rapids'});
	currentArray.append({'name':'RES Aegis Nova', 'link':'/mosaic/9568', 'city':'Saint Paul'});
	currentArray.append({'name':'Flight', 'link':'/mosaic/9573', 'city':'Minneapolis'});
	currentArray.append({'name':'Saint Paul Park  Minnesota', 'link':'/mosaic/9753', 'city':'Saint Paul Park'});
	currentArray.append({'name':'ENL Aegis Nova', 'link':'/mosaic/9754', 'city':'Saint Paul'});
	currentArray.append({'name':'Visit RiverSouth', 'link':'/mosaic/9837', 'city':'Prior Lake'});
	currentArray.append({'name':'Ingress LEGO', 'link':'/mosaic/10034', 'city':'Minneapolis'});
	currentArray.append({'name':'Spring Monster - Victory Memorial Pkwy', 'link':'/mosaic/10080', 'city':'Minneapolis'});
	currentArray.append({'name':'Aegis Nova Saint Paul', 'link':'/mosaic/10728', 'city':'Saint Paul'});
	currentArray.append({'name':'Victory Memorial Parkway Summer', 'link':'/mosaic/10874', 'city':'Minneapolis'});
	currentArray.append({'name':'Assist ADA', 'link':'/mosaic/11043', 'city':'Minneapolis'});
	currentArray.append({'name':'Enlightened Aegis Nova Saint Paul', 'link':'/mosaic/11096', 'city':'Saint Paul'});
	currentArray.append({'name':'Owatonna  Minnesota', 'link':'/mosaic/11309', 'city':'Owatonna'});
	currentArray.append({'name':'Explore Cottage Grove', 'link':'/mosaic/11330', 'city':'Cottage Grove'});
	currentArray.append({'name':'Thanks MSP from WI ENL', 'link':'/mosaic/11357', 'city':'Saint Paul'});
	currentArray.append({'name':'Visit Lake Calhoun', 'link':'/mosaic/11679', 'city':'Minneapolis'});
	currentArray.append({'name':'Couch - The Lazy Frog', 'link':'/mosaic/11715', 'city':'Saint Paul'});
	currentArray.append({'name':'Lounge - The Lazy Frog', 'link':'/mosaic/11720', 'city':'Saint Paul'});
	currentArray.append({'name':'What is Love  - The Lazy Frog', 'link':'/mosaic/11734', 'city':'Saint Paul'});
	currentArray.append({'name':'Centennial Lakes Park', 'link':'/mosaic/12182', 'city':'Minneapolis'});
	currentArray.append({'name':'Jordan Belle Plaine', 'link':'/mosaic/12218', 'city':'Jordan'});
	currentArray.append({'name':'Fantasy Fun at The Fair', 'link':'/mosaic/12492', 'city':'Saint Paul'});
	currentArray.append({'name':'Farmington Discovery', 'link':'/mosaic/12493', 'city':'Farmington'});
	currentArray.append({'name':'Minnesota State University  Mankato', 'link':'/mosaic/12494', 'city':'Mankato'});
	currentArray.append({'name':'Lake Minnetonka', 'link':'/mosaic/12667', 'city':'Excelsior'});
	currentArray.append({'name':'Part C  Cosmic Castles', 'link':'/mosaic/12825', 'city':'Minneapolis'});
	currentArray.append({'name':'Johnson  Minnesota', 'link':'/mosaic/13400', 'city':'Mankato'});
	currentArray.append({'name':'I m On A Boat', 'link':'/mosaic/13806', 'city':'Minneapolis'});
	currentArray.append({'name':'Don t tread on me', 'link':'/mosaic/14295', 'city':'Saint Paul'});
	currentArray.append({'name':'Zen Herny the Lazy Frog', 'link':'/mosaic/14296', 'city':'Inver Grove Heights'});
	currentArray.append({'name':'walking the Mall of America', 'link':'/mosaic/14786', 'city':'Bloomington'});
	currentArray.append({'name':'twin ports tour', 'link':'/mosaic/14884', 'city':'Duluth'});
	currentArray.append({'name':'Blue Giants', 'link':'/mosaic/16108', 'city':'Mankato'});
	currentArray.append({'name':'Fall Monster - Victory Memorial Pkwy', 'link':'/mosaic/16110', 'city':'Minneapolis'});
	currentArray.append({'name':'FSM s Loring Park', 'link':'/mosaic/16217', 'city':'Minneapolis'});
	currentArray.append({'name':'Another Galaxy Purple Planets', 'link':'/mosaic/16366', 'city':'Saint Paul'});
	currentArray.append({'name':'Shakopee  Minnesota', 'link':'/mosaic/17078', 'city':'Shakopee'});
	currentArray.append({'name':'The Great North Shore Adventure', 'link':'/mosaic/17394', 'city':'Duluth'});
	currentArray.append({'name':'Minneapolis Grain Exchange', 'link':'/mosaic/18248', 'city':'Minneapolis'});
	currentArray.append({'name':'County Road 42 Hack', 'link':'/mosaic/19821', 'city':'Rosemount'});
	currentArray.append({'name':'Walking Lake Phalen', 'link':'/mosaic/20688', 'city':'Saint Paul'});
	currentArray.append({'name':'ENL Frog', 'link':'/mosaic/21324', 'city':'Saint Paul'});
	currentArray.append({'name':'Peanuts', 'link':'/mosaic/22383', 'city':'Saint Paul'});
	currentArray.append({'name':'A Walk Around the Lake and Conservatory', 'link':'/mosaic/22424', 'city':'Saint Paul'});
	currentArray.append({'name':'darth vader', 'link':'/mosaic/22771', 'city':'Duluth'});
	currentArray.append({'name':'White Bear Lake', 'link':'/mosaic/23120', 'city':'White Bear Lake'});
	currentArray.append({'name':'All of My Purple Life', 'link':'/mosaic/23417', 'city':'Chanhassen'});
	currentArray.append({'name':'Leia s Tribute', 'link':'/mosaic/23418', 'city':'Minneapolis'});
	currentArray.append({'name':'2017 The Spring Monster', 'link':'/mosaic/23668', 'city':'Minneapolis'});
	currentArray.append({'name':'Mendota Heights Area', 'link':'/mosaic/25515', 'city':'Saint Paul'});
	currentArray.append({'name':'The Puppet Master', 'link':'/mosaic/26664', 'city':'New Ulm'});
	currentArray.append({'name':'Farmtown Hack', 'link':'/mosaic/27343', 'city':'Farmington'});
	currentArray.append({'name':'in Faribault  MN Mural', 'link':'/mosaic/510', 'city':'Faribault'});
	currentArray.append({'name':'viking Stadium', 'link':'/mosaic/1250', 'city':'Minneapolis'});
	currentArray.append({'name':'ZP SUPERHERO FARIBAULT MURAL', 'link':'/mosaic/3293', 'city':'Faribault'});
	currentArray.append({'name':'FALL IN LOVE WITH LEAVES', 'link':'/mosaic/3296', 'city':'Prior Lake'});
	currentArray.append({'name':'Bike the Grand Rounds', 'link':'/mosaic/3308', 'city':'Minneapolis'});
	currentArray.append({'name':'St Paul Skyline', 'link':'/mosaic/3312', 'city':'Saint Paul'});
	currentArray.append({'name':'Mississippi Riverfront', 'link':'/mosaic/3317', 'city':'Minneapolis'});
	currentArray.append({'name':'Duluth Lift Bridge', 'link':'/mosaic/3325', 'city':'Duluth'});
	currentArray.append({'name':'Greetings From Austin', 'link':'/mosaic/5857', 'city':'Austin'});
	currentArray.append({'name':'Spam Mural - Austin  Minnesota', 'link':'/mosaic/5898', 'city':'Austin'});
	currentArray.append({'name':'Minneapolis Remembers Prince', 'link':'/mosaic/9539', 'city':'Minneapolis'});
	currentArray.append({'name':'Exploring Woodbury', 'link':'/mosaic/9540', 'city':'Saint Paul'});
	currentArray.append({'name':'Mining the Iron Range', 'link':'/mosaic/9878', 'city':'Grand Rapids'});
	currentArray.append({'name':'Quarry Hill Nature Center', 'link':'/mosaic/9880', 'city':'Rochester'});
	currentArray.append({'name':'Nightmare before Anoka-mas', 'link':'/mosaic/10875', 'city':'Anoka'});
	currentArray.append({'name':'Twin Cities Pride', 'link':'/mosaic/12246', 'city':'Minneapolis'});
	currentArray.append({'name':'Deer Me (Winona  Mn)', 'link':'/mosaic/13496', 'city':'Winona'});
	currentArray.append({'name':'Tribute to Abraham Lincoln', 'link':'/mosaic/13574', 'city':'Minneapolis'});
	currentArray.append({'name':'Winona Interstate Bridge', 'link':'/mosaic/14072', 'city':'Winona'});
	currentArray.append({'name':'death star', 'link':'/mosaic/14373', 'city':'Shafer'});
	currentArray.append({'name':'Majestic Unicorn', 'link':'/mosaic/17338', 'city':'Duluth'});
	currentArray.append({'name':'Victory Memorial Parkway Winter 2017', 'link':'/mosaic/19091', 'city':'Minneapolis'});
	currentArray.append({'name':'1   12 - Red Apple', 'link':'/mosaic/20736', 'city':'Saint Paul'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart (STP)', 'link':'/mosaic/22135', 'city':'Saint Paul'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart (STP)v2 1a', 'link':'/mosaic/22567', 'city':'Saint Paul'});
	currentArray.append({'name':'The Alphabet', 'link':'/mosaic/17067', 'city':'Minneapolis'});
	currentArray.append({'name':'Savage Factions Mural', 'link':'/mosaic/9009', 'city':'Savage'});
	currentArray.append({'name':'Operation #MINOTAUR', 'link':'/mosaic/12654', 'city':'Minneapolis'});
	currentArray.append({'name':'Arbo s Birches', 'link':'/mosaic/16365', 'city':'Chaska'});
	currentArray.append({'name':'The Fabulous Fever', 'link':'/mosaic/17339', 'city':'Duluth'});
	currentArray.append({'name':'State of Hockey', 'link':'/mosaic/3306', 'city':'Bloomington'});
	currentArray.append({'name':'State Fair Fairchild', 'link':'/mosaic/3319', 'city':'Saint Paul'});
	currentArray.append({'name':'St Paul  Minnesota', 'link':'/mosaic/9756', 'city':'Saint Paul'});
	currentArray.append({'name':'Cosmic Castles', 'link':'/mosaic/10451', 'city':'Minneapolis'});
	currentArray.append({'name':'Paul Bunyan Mural - Saint Cloud', 'link':'/mosaic/3322', 'city':'Saint Cloud'});
	currentArray.append({'name':'Uptown Say Anything', 'link':'/mosaic/20071', 'city':'Minneapolis'});
	currentArray.append({'name':'Green - 2014 State Fair Banner Art', 'link':'/mosaic/24237', 'city':'Saint Paul'});
	currentArray.append({'name':'Valley of The Jolly  Green Giant', 'link':'/mosaic/3291', 'city':'Mankato'});
	currentArray.append({'name':'2011  Fair Banner Tribute', 'link':'/mosaic/25664', 'city':'Saint Paul'});
	currentArray.append({'name':'Let s Put A Smile On That Face', 'link':'/mosaic/14294', 'city':'Minneapolis'});
	currentArray.append({'name':'VMP  - BATMAN', 'link':'/mosaic/18657', 'city':'Minneapolis'});

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
