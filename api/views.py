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
					data.append({'mid':item['mid'], 'status': 'incomplete', 'mosaicref':m.mosaic.ref, 'startLat':m.startLat, 'startLng':m.startLng})
				else:
					data.append({'mid':item['mid'], 'status': 'completed', 'mosaicref':m.mosaic.ref, 'startLat':m.startLat, 'startLng':m.startLng})
			else:
				if m.admin == True:
					data.append({'mid':item['mid'], 'status': 'registered', 'startLat':m.startLat, 'startLng':m.startLng})
				else:
					data.append({'mid':item['mid'], 'status': 'hidden', 'startLat':m.startLat, 'startLng':m.startLng})
					
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
			mission.admin = True
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
	
	if not request.user.is_anonymous and request.user.profile:
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
	
	results = Mission.objects.filter(mosaic__isnull = True, admin=True).order_by('title')
	if results.count() > 0:
		
		missions = []
		for item in results:
			
			temp = item.overviewSerialize()
			missions.append(temp)
	
	return Response(missions, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_searchForMissions(request):
	
	data = { 'missions': [], }

	results = Mission.objects.filter(mosaic__isnull=True, admin=True).filter(Q(title__icontains=request.data['text']) | Q(creator__icontains=request.data['text']))
	if results.count() > 0:
		for mission in results:
			data['missions'].append(mission.overviewSerialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_create(request):
	
	results = Country.objects.filter(name=request.data['country'])
	if results.count() > 0:
		country = results[0]
	else:
		country = Country(name=request.data['country'])
		country.save()
		
	results = Region.objects.filter(country=country, name=request.data['region'])
	if results.count() > 0:
		region = results[0]
	else:
		region = Region(country=country, name=request.data['region'])
		region.save()
		
	results = City.objects.filter(region=region, name=request.data['city'])
	if results.count() > 0:
		city = results[0]
	else:
		city = City(region=region, name=request.data['city'])
		city.save()
		
	mosaic = Mosaic(	registerer = request.user,
						cols = int(request.data['columns']),
						type = request.data['type'],
						city = city,
						title = request.data['title']
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
	mosaic.generatePreview()
	
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
		
		results = Country.objects.filter(name=request.data['city']['region']['country']['name'])
		if results.count() > 0:
			country = results[0]
		else:
			country = Country(name=request.data['city']['region']['country']['name'])
			country.save()
			
		results = Region.objects.filter(country=country, name=request.data['city']['region']['name'])
		if results.count() > 0:
			region = results[0]
		else:
			region = Region(country=country, name=request.data['city']['region']['name'])
			region.save()
			
		results = City.objects.filter(country=country, region=region, name=request.data['city']['name'])
		if results.count() > 0:
			city = results[0]
		else:
			city = City(country=country, region=region, name=request.data['city']['name'])
			city.save()
			
		mosaic.city = city
		mosaic.type = request.data['type']
		mosaic.cols = request.data['cols']
		mosaic.title = request.data['title']
		mosaic.region = region
		mosaic.country = country
		
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
	
		mosaic.computeInternalData()
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
			
			mosaic.computeInternalData()
			mosaic.save()
			
			data = mosaic.detailsSerialize()
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
		
		if request.data['mission'] == 'Unavailable':
			
			item = Mission(data='{}', title='Fake mission', ref='Unavailable-' + request.data['order'] + mosaic.ref, mosaic=mosaic, order=request.data['order'])
			item.save()
			
		else:
			
			result = Mission.objects.filter(ref=request.data['mission'], mosaic__isnull=True)
			if result.count() > 0:
				
				mission = result[0]
				
				mission.mosaic = mosaic
				mission.order = request.data['order']
				mission.save()
			
		mosaic.computeInternalData()
		mosaic.save()
		
		data = mosaic.detailsSerialize()
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
	
	results = Country.objects.all()
	if (results.count() > 0):
		
		data = {
			'count': 0,
			'countries': [],
		}
		
		for item in results:
			
			country = {
				'mosaics': Mosaic.objects.filter(city__region__country=item).count(),
				'name': item.name,
				'locale': item.locale,
				'id': item.pk,
			}
			
			data['countries'].append(country)
			
		data['count'] = Mosaic.objects.all().count()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByRegion(request, name):
	
	data = None
	
	country = Country.objects.get(name=name)

	results = Region.objects.filter(country__name=name)
	if (results.count() > 0):
		
		data = {
			'count': 0,
			'country': country.serialize(),
			'regions': [],
		}
		
		for item in results:
			
			region = {
				'mosaics': Mosaic.objects.filter(city__region=item).count(),
				'name': item.name,
				'locale': item.locale,
				'id': item.pk,
			}
			
			data['regions'].append(region)
	
		data['count'] = Mosaic.objects.filter(city__region__country__name=name).count()
	
	return Response(data, status=status.HTTP_200_OK)
	


#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByCity(request, country, name):
	
	data = None
	
	country = Country.objects.get(name=country)
	region = Region.objects.get(country=country, name=name)
	
	results = City.objects.filter(region__country__name=country, region__name=name)
	if (results.count() > 0):
		
		data = {
			'count': 0,
			'country': country.serialize(),
			'region': region.serialize(),
			'cities': [],
		}
		
		for item in results:
			
			city = {
				'mosaics': item.mosaics.count(),
				'name': item.name,
				'locale': item.locale,
				'id': item.pk,
			}
			
			data['cities'].append(city)
	
		data['count'] = Mosaic.objects.filter(city__region__name=name).count()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsOfCity(request, country, region, name):
	
	country = Country.objects.get(name=country)
	region = Region.objects.get(country=country, name=region)
	city = City.objects.get(region=region, name=name)
	
	results = Mosaic.objects.filter(city=city).order_by('-pk')
	if results.count() > 0:
		
		data = {
			'count': 0,
			'country': country.serialize(),
			'region': region.serialize(),
			'city': city.serialize(),
			'mosaics': [],
		}
		
		for item in results:
			
			mosaic = item.overviewSerialize()
			data['mosaics'].append(mosaic)
		
		return Response(data, status=status.HTTP_200_OK)
		
	return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def data_searchForMissions(request):
	
	results = Mission.objects.filter(mosaic__isnull=True, registerer='FIiptart').update(registerer='RivmanBX')
	
	results = Mission.objects.filter(mosaic__isnull=True, registerer=request.user, admin=True)
	if (results.count() > 0):

		data = { 'missions': [], }
		for item in results:
			data['missions'].append(item.overviewSerialize())

		if request.user.is_superuser:
			Mission.objects.filter(mosaic__isnull=True, registerer__isnull=True).delete()

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
	
	results = Mosaic.objects.filter(Q(city__region__country__name__icontains=request.data['text']) | Q(city__region__country__locale__icontains=request.data['text']))
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
		
	# Region search
	
	results = Mosaic.objects.filter(Q(city__region__name__icontains=request.data['text']) | Q(city__region__locale__icontains=request.data['text']))
	if (results.count() > 0):
		for mosaic in results:
			array.append(mosaic)
		
	# City search
	
	results = Mosaic.objects.filter(Q(city__name__icontains=request.data['text']) | Q(city__locale__icontains=request.data['text']))
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
	results = Mission.objects.filter(mosaic__isnull=True, registerer=request.user, admin=True).values(fieldname).order_by(fieldname).annotate(count=Count(fieldname)).order_by('-count')
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
def data_getPotentialMissionByName(request):
	
	data = None

	results = Mission.objects.filter(mosaic__isnull=True, registerer=request.user, admin=True, name=request.data['name'])
	if (results.count() > 0):
		
		data = []
		
		for item in results:
			data.append(item.overviewSerialize())
				
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def data_getOpportunities(request):
	
	data = []
	
	currentArray = []

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



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def event_view(request):
	
	data = { 'cities':[], }
	
	results = Mosaic.objects.filter(tags__icontains=request.data['event'])
	if results.count() > 0:
		
		obj = { 'mosaics':[], }
		data['cities'].append(obj)
	
		for item in data['cities']:
			for mosaic in results:
				item['mosaics'].append(mosaic.overviewSerialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def country_getList(request):
	
	data = { 'countries': [], }
	
	results = Country.objects.all()
	for item in results:
		data['countries'].append(item.serialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def country_create(request):
	
	item = Country(name=request.data['name'])
	item.save()
	
	data = { 'country': item.serialize(), }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def country_update(request):
	
	item = Country.objects.get(pk=request.data['id'])
	item.name = request.data['new_name']
	item.locale = request.data['new_locale']
	item.save()
	
	data = { 'country': item.serialize(), }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_getListFromCountry(request):
	
	data = { 'regions': [], }
	
	results = Region.objects.filter(country__pk=request.data['country_id'])
	for item in results:
		data['regions'].append(item.serialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_create(request):
	
	item = Region(country__pk=request.data['country_id'], name=request.data['name'])
	item.save()
	
	data = { 'region': item.serialize(), }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_update(request):
	
	item = Region.objects.get(pk=request.data['id'])
	item.name = request.data['new_name']
	item.locale = request.data['new_locale']
	item.save()
	
	data = { 'region': item.serialize(), }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_move(request):
	
	src = Region.objects.get(pk=request.data['src_id'])
	dest = Region.objects.get(pk=request.data['dest_id'])
	
	for item in Mosaic.objects.filter(city__region=src):
		item.city.region = dest
		item.save()

	src.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_getListFromCountryRegion(request):
	
	data = { 'cities': [], }
	
	results = City.objects.filter(region__pk=request.data['region_id'])
	for item in results:
		data['cities'].append(item.serialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_create(request):
	
	item = City(country__pk=request.data['country_id'], region__pk=request.data['region_id'], name=request.data['name'])
	item.save()
	
	data = { 'city': item.serialize(), }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_update(request):
	
	item = City.objects.get(pk=request.data['id'])
	item.name = request.data['new_name']
	item.locale = request.data['new_locale']
	item.save()
	
	data = { 'city': item.serialize(), }
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_move(request):
	
	src = City.objects.get(pk=request.data['src_id'])
	dest = City.objects.get(pk=request.data['dest_id'])
	
	for item in src.mosaics.all():
		item.city = dest
		item.save()

	src.delete()
	
	return Response(None, status=status.HTTP_200_OK)
