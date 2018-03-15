#!/usr/bin/env python
# coding: utf-8

import json
import urllib
import requests

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token

from rest_social_auth.serializers import UserTokenSerializer

from .models import *

from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.db.models import Q
from django.db.models import Count

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model, authenticate, logout, login

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
				data.append({'mid':item['mid'], 'name':m.title, 'status': 'registered', 'startLat':m.startLat, 'startLng':m.startLng})

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
ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
REDIRECT_URL = 'https://www.myingressmosaics.com'
USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_google(request):
	
	code = request.data['code']
	
	params = {
		'code': code,
		'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
		'grant_type': 'authorization_code', 
		'redirect_uri': REDIRECT_URL,
		'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
	}
	
	response = requests.post(ACCESS_TOKEN_URL, data=params)
	if response.status_code != 200:
		raise(Exception('ACCESS_TOKEN - Invalid response, response code {c}'.format(c=response.status_code)))
	
	access_token = response.json()['access_token']
	
	params = urllib.parse.urlencode({'access_token': access_token})
	response = requests.get(USER_INFO_URL + '?' + params)
	if response.status_code != 200:
		raise(Exception('USER_INFO - Invalid response, response code {c}'.format(c=response.status_code)))
	
	userInfo = response.json()
	print(userInfo)
	
	email = userInfo['email']
	
	try:
		name = userInfo['given_name']
		user = User.objects.get(username=name, email=email)
		
	except User.DoesNotExist:
		
		try:
			name = userInfo['name']
			user = User.objects.get(username=name, email=email)
	
		except User.DoesNotExist:
		
			try:
				name = userInfo['given_name']
				user = User.objects.create_user(name, email, 'password')
	
			except:
				name = userInfo['name']
				user = User.objects.create_user(name, email, 'password')
				
			user.first_name = name
			user.last_name = userInfo['family_name']
			user.save()
			
			user.profile.family_name = userInfo['family_name']
			user.profile.picture = userInfo['picture']
			user.profile.locale = userInfo['locale']
			user.profile.save()
			
			Token.objects.get_or_create(user=user)
	
	user = authenticate(username=name, password='password')
	login(request, user)
	
	return Response(UserTokenSerializer(user).data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_login(request):
	
	user = authenticate(username=request.data['username'], password=request.data['password'])
	if user is None:
		return Response('error_USER_UNKNOWN', status=status.HTTP_400_BAD_REQUEST)
	
	login(request, user)
	
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
@permission_classes((AllowAny, ))
def user_getDetails(request):
	
	data = {
		'mosaics': [],
		'missions': [],
		'like': [],
		'todo': [],
		'complete': [],
		'notif': [],
	}
	
	if not request.user.is_anonymous:
		
		results = Mosaic.objects.filter(creators__contains=request.user.username)
		if results.count() > 0:
			for item in results:
				
				mosaic = item.overviewSerialize()
				data['mosaics'].append(mosaic)
		
		results = Mission.objects.filter(mosaic__isnull=True, creator=request.user.username)
		if results.count() > 0:
			for item in results:
				
				mission = item.overviewSerialize()
				data['missions'].append(mission)
		
		results = Link.objects.filter(user=request.user, type='like')
		if results.count() > 0:
			for item in results:
				
				mosaic = item.mosaic.overviewSerialize()
				data['like'].append(mosaic)
		
		results = Link.objects.filter(user=request.user, type='todo')
		if results.count() > 0:
			for item in results:
				
				mosaic = item.mosaic.overviewSerialize()
				data['todo'].append(mosaic)
		
		results = Link.objects.filter(user=request.user, type='complete')
		if results.count() > 0:
			for item in results:
				
				mosaic = item.mosaic.overviewSerialize()
				data['complete'].append(mosaic)
		
		results = Notif.objects.filter(user=request.user)
		if results.count() > 0:
			for item in results:
				
				notif = { 'country_name':item.country.name, 'region_name':None, 'city_name':None }
				if item.region: notif['region_name'] = item.region.name
				if item.city: notif['city_name'] = item.city.name
				data['notif'].append(notif)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def user_getProfile(request):
	
	data = {
		'name': request.user.username,
		'faction': None,
		'picture': None,
		'superuser': request.user.is_superuser,
	}
	
	if not request.user.is_anonymous and request.user.profile:
		data['faction'] = request.user.profile.faction
		data['picture'] = request.user.profile.picture
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def user_edit(request):
	
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
	
	results = Potential.objects.filter(title=request.data['title'], city = city)
	if results.count() > 0:
		results[0].delete()
	
	country_notifiers = Notif.objects.filter(country=country, region__isnull=True, city__isnull=True).values_list('user__email')
	region_notifiers = Notif.objects.filter(country=country, region=region, city__isnull=True).values_list('user__email')
	city_notifiers = Notif.objects.filter(country=country, region=region, city=city).values_list('user__email')
	
	receivers = []
	for item in country_notifiers: receivers.append(item[0])
	for item in region_notifiers: receivers.append(item[0])
	for item in city_notifiers: receivers.append(item[0])
	receivers = set(receivers)
	receivers = list(receivers)

	if len(receivers) > 0:
		
		msg_plain = render_to_string('new_mosaic.txt', { 'ref':mosaic.ref, 'name':mosaic.title, 'count':mosaic.missions.all().count(), 'country':country.name, 'region':region.name, 'city':city.name })
		
		for receiver in receivers:
			send_mail(
				'[MIM] New Mosaic Registered',
		    	msg_plain,
		    	'admin@myingressmosaics.com',
		    	[receiver],
		    	fail_silently=False,
		    )
	
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
		
		data['is_like'] = False
		data['is_todo'] = False
		data['is_complete'] = False
		
		if not request.user.is_anonymous:
			
			if Link.objects.filter(mosaic=mosaic, user=request.user, type='like').count() > 0:
				data['is_like'] = True

			if Link.objects.filter(mosaic=mosaic, user=request.user, type='todo').count() > 0:
				data['is_todo'] = True

			if Link.objects.filter(mosaic=mosaic, user=request.user, type='complete').count() > 0:
				data['is_complete'] = True

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
		
		results = Country.objects.filter(name=request.data['country_name'])
		if results.count() > 0:
			country = results[0]
		else:
			country = Country(name=request.data['country_name'])
			country.save()
			
		results = Region.objects.filter(country=country, name=request.data['region_name'])
		if results.count() > 0:
			region = results[0]
		else:
			region = Region(country=country, name=request.data['region_name'])
			region.save()
			
		results = City.objects.filter(region=region, name=request.data['city_name'])
		if results.count() > 0:
			city = results[0]
		else:
			city = City(region=region, name=request.data['city_name'])
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
def mosaic_link(request):
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		
		result = mosaic.links.filter(user=request.user, type=request.data['type'])
		if result.count() < 1:
			
			link = Link(mosaic=mosaic, user=request.user, type=request.data['type'])
			link.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mosaic_unlink(request):
	
	result = Mosaic.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mosaic = result[0]
		
		result = mosaic.links.filter(user=request.user, type=request.data['type'])
		if result.count() > 0:
			
			link = result[0]
			link.delete()
	
	return Response(None, status=status.HTTP_200_OK)



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
def mission_update(request):
	
	data = { 'mission':None, }
	
	result = Mission.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mission = result[0]
		
		mission.title = request.data['title']
		mission.order = request.data['order']
		mission.save()
		
		data['mission'] = mission.detailsSerialize()
		
	return Response(data, status=status.HTTP_200_OK)
	
	
	
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def mission_details(request):
	
	data = { 'mission':None, }
	
	result = Mission.objects.filter(ref=request.data['ref'])
	if result.count() > 0:
		
		mission = result[0]
		
		data['mission'] = mission.detailsSerialize()
		
	return Response(data, status=status.HTTP_200_OK)
	
	
	
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
	
	data = {
		'mosaic_count': Mosaic.objects.all().count(),
		'countries': [],
	}
	
	results = Country.objects.all();
	for country in results:
		
		item_data = {
			'name':country.name,
			'code':country.code,
			'locale':country.locale,
			'mosaic_count':Mosaic.objects.filter(city__region__country=country).count(),
		}
		
		data['countries'].append(item_data)

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
			'notified': False,
		}
		
		for item in results:
			
			mosaic_count = Mosaic.objects.filter(city__region=item).count()
			potential_count = Potential.objects.filter(city__region=item).count()
			
			if mosaic_count > 0 or potential_count > 0:
				region = {
					'mosaics': mosaic_count,
					'potentials': potential_count,
					'name': item.name,
					'locale': item.locale,
					'id': item.pk,
				}
				
				data['regions'].append(region)
		
		data['count'] = Mosaic.objects.filter(city__region__country__name=name).count()
		
		if request.user.is_authenticated:
			notif_results = Notif.objects.filter(user=request.user, country=country, region__isnull=True, city__isnull=True)
			if notif_results.count() > 0:
				data['notified'] = True
	
	return Response(data, status=status.HTTP_200_OK)


#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByCity(request, country, name):
	
	data = None
	
	country = Country.objects.get(name=country)
	region = Region.objects.get(country=country, name=name)
	
	results = City.objects.filter(region=region).order_by('name')
	if (results.count() > 0):
		
		data = {
			'count': 0,
			'country': country.serialize(),
			'region': region.serialize(),
			'cities': [],
			'notified': False,
		}
		
		for item in results:
			
			city = {
				'mosaics': item.mosaics.all().count(),
				'name': item.name,
				'locale': item.locale,
				'id': item.pk,
			}
			
			data['cities'].append(city)
	
		data['count'] = Mosaic.objects.filter(city__region=region).count()
		
		if request.user.is_authenticated:
			notif_results = Notif.objects.filter(user=request.user, country=country, region=region, city__isnull=True)
			if notif_results.count() > 0:
				data['notified'] = True
		
	return Response(data, status=status.HTTP_200_OK)
	


#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def newdata_getMosaicsByCity(request, country_name, region_name):
	
	data = {
		'region': None,
		
		'cities': [],
		'mosaics': [],
		'potentials': [],
		
		'location_indexes': [],
	}
	
	# Region data
	region_obj = Region.objects.get(country__name=country_name, name=region_name)
	
	data['region'] = {
		'country_code':region_obj.country.code,
		'country_name':region_obj.country.name,
		'name':region_obj.name,
		'mosaic_count':0,
		'potential_count':0,
		'notified':False,
	}
	
	if request.user.is_authenticated:
		notif_results = Notif.objects.filter(user=request.user, country=region_obj.country, region=region_obj, city__isnull=True)
		if notif_results.count() > 0:
			data['region']['notified'] = True

	# Cities data
	for city_obj in region_obj.cities.all():
	
		city_data = {
			'name':city_obj.name,
			'locale':city_obj.locale,
			'mosaic_count': 0,
			'potential_count': 0,
		}
		
		data['cities'].append(city_data)

		# Locations indexes data
		location_index = city_obj.name[0]
		if location_index not in data['location_indexes']:
			data['location_indexes'].append(location_index)
		
		# Mosaics data
		mosaics = city_obj.mosaics.all()
		for mosaic_obj in mosaics:
		
			mosaic_data = {
				'ref':mosaic_obj.ref,
				'cols':mosaic_obj.cols,
				'title':mosaic_obj.title,
				'uniques':mosaic_obj.uniques,
				'city_name':mosaic_obj.city.name,
				'mission_count':0,
				
				'images':[],
			}
			
			data['mosaics'].append(mosaic_data)
			
			for mission_obj in mosaic_obj.missions.all().order_by('-order'):
				mosaic_data['images'].append(mission_obj.image)
				mosaic_data['mission_count'] += 1
			
			city_data['mosaic_count'] += 1
			
			data['region']['mosaic_count'] += 1
		
		# Potentials data
		potentials = city_obj.potentials.all()
		for potential_obj in potentials:
			
			potential_data = potential_obj.overviewSerialize()
			data['potentials'].append(potential_data)
			
			city_data['potential_count'] += 1
			
			data['region']['potential_count'] += 1
			
	data['location_indexes'].sort()
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsOfCity(request, country, region, name):
	
	data = {
		'city': {},
		'potentials': [],
		'mosaics': [],
		'notified': False,
	}
			
	results = Country.objects.filter(name=country)
	if results.count() > 0:
		country = results[0]
	
		results = Region.objects.filter(country=country, name=region)
		if results.count() > 0:
			region = results[0]
		
			results = City.objects.filter(region=region, name=name)
			if results.count() > 0:
				city = results[0]
				
				data['city'] = city.serialize()
				
				results = Mosaic.objects.filter(city=city).order_by('title')
				if results.count() > 0:
					
					for item in results:
						
						mosaic = item.overviewSerialize()
						data['mosaics'].append(mosaic)
						
				results = Potential.objects.filter(city=city).order_by('title')
				if results.count() > 0:
					
					for item in results:
						
						potential = item.overviewSerialize()
						data['potentials'].append(potential)
				
						
	if len(data['mosaics']) < 1 and len(data['potentials']) < 1 and not request.user.is_superuser:
		search = Search(city=name, region=region, country=country)
		search.save()
		
	if request.user.is_authenticated:
		notif_results = Notif.objects.filter(user=request.user, country=city.region.country, region=city.region, city=city)
		if notif_results.count() > 0:
			data['notified'] = True
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes((AllowAny, ))
def data_getMosaicsByCreator(request, name):
	
	data = {
		'name': name,
		'faction': None,
		'mosaics': [],
		'missions': [],
	}
	
	result = Mission.objects.filter(creator=name)
	if result.count() > 0:
		data['faction'] = result[0].faction

	result = Mosaic.objects.filter(creators__contains=name).order_by('city__name', 'title')
	for item in result:
		data['mosaics'].append(item.overviewSerialize())

	result = Mission.objects.filter(mosaic__isnull=True, creator=name).order_by('title')
	for item in result:
		data['missions'].append(item.overviewSerialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def data_missionsByName(request):
	
	data = {
		'missions': [],
	}
	
	results = Mission.objects.filter(mosaic__isnull=True, name=request.data['name'])
	for item in results:
		data['missions'].append(item.overviewSerialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def data_searchForMissions(request):
	
	data = { 'missions': [], }
	
	names = []
	
	fieldname = 'name'
	results = Mission.objects.filter(mosaic__isnull=True, admin=True).order_by(fieldname).values(fieldname).annotate(count=Count(fieldname)).order_by('count', 'name')
	for item in results:
		if item['count'] >= 3:
			names.append(item['name'])
	
	results = Mission.objects.filter(mosaic__isnull=True, name__in=names).order_by('name')
	for item in results:
		data['missions'].append(item.overviewSerialize())
			
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def data_newSearchForMissions(request):
	
	data = {
		'missions': [],
		'potential': None,
	}
	
	results = Mission.objects.filter(mosaic__isnull=True).filter(Q(name__icontains=request.data['text']) | Q(title__icontains=request.data['text']) | Q(creator__icontains=request.data['text']))
	if (results.count() > 0):
		for item in results:
			data['missions'].append(item.overviewSerialize())

	results = Potential.objects.filter(title=request.data['text'])
	if (results.count() > 0):
		
		potential = results[0]
		
		if len(data['missions']) > 0:
			data['potential'] = {
				'city': potential.city.serialize(),
				'title': potential.title,
				'count': potential.count,
			}
			
		else:
			potential.delete()
	
	return Response(data, status=status.HTTP_200_OK)
	
	
	
#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def data_searchForMosaics(request):
	
	data = {
		'mosaics': [],
		'potentials': [],
		'missions': [],
	}
	
	mosaic_array = []
	
	# Creator search
	
	results = Mosaic.objects.filter(creators__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			mosaic_array.append(mosaic)
		
	# Title search
	
	results = Mosaic.objects.filter(title__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			mosaic_array.append(mosaic)
		
	# City search
	
	results = Mosaic.objects.filter(city__name__icontains=request.data['text'])
	if (results.count() > 0):
		for mosaic in results:
			mosaic_array.append(mosaic)
	
	if (len(mosaic_array) > 0):
		
		temp = list(set(mosaic_array))[:25]
		
		for item in temp:
			data['mosaics'].append(item.overviewSerialize())
	
	potential_array = []
	
	# Creator search
	
	results = Potential.objects.filter(creator__icontains=request.data['text'])
	if (results.count() > 0):
		for potential in results:
			potential_array.append(potential)
		
	# Title search
	
	results = Potential.objects.filter(title__icontains=request.data['text'])
	if (results.count() > 0):
		for potential in results:
			potential_array.append(potential)
		
	# City search
	
	results = Potential.objects.filter(city__name__icontains=request.data['text'])
	if (results.count() > 0):
		for potential in results:
			potential_array.append(potential)
	
	if (len(potential_array) > 0):
		
		temp = list(set(potential_array))[:25]
		
		for item in temp:
			data['potentials'].append(item.overviewSerialize())
	
	mission_array = []
	
	# Creator search
	
	results = Mission.objects.filter(mosaic__isnull=True, creator__icontains=request.data['text'])
	if (results.count() > 0):
		for mission in results:
			mission_array.append(mission)
		
	# Title search
	
	results = Mission.objects.filter(mosaic__isnull=True, title__icontains=request.data['text'], validated=False)
	if (results.count() > 0):
		for mission in results:
			mission_array.append(mission)
		
	# Name search
	
	results = Mission.objects.filter(mosaic__isnull=True, name__icontains=request.data['text'], validated=False)
	if (results.count() > 0):
		for mission in results:
			mission_array.append(mission)
			
	if (len(mission_array) > 0):
		
		temp = list(set(mission_array))[:50]
		
		for item in temp:
			data['missions'].append(item.overviewSerialize())
			
	if (len(mission_array) < 1) and (len(mosaic_array) < 1):

		if not request.user.is_superuser:
			search = Search(name=request.data['text'])
			search.save()
			
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
			
			mosaic = item.overviewSerialize()
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
def potential_getAll(request):
	
	data = []

	countries = Country.objects.all().order_by('name')
	for country in countries:
		potentials_results = country.potentials.order_by('city__name', '-count', 'title')
		
		if potentials_results.count() > 0:
			
			obj = { 'name':country.name, 'potentials':[], 'open':False, }
			
			for potential in potentials_results:
				
				obj['potentials'].append({
					'city': potential.city.serialize(),
					'title': potential.title,
					'count': potential.count,
				})
			
			if len(obj['potentials']) > 0:
				data.append(obj)

	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_detect(request):

	data = []
	
	from django.db.models import Count
	
	fieldname = 'name'
	results = Mission.objects.filter(mosaic__isnull=True, admin=True, validated=False).order_by(fieldname).values(fieldname, 'creator').annotate(count=Count(fieldname)).order_by('creator', '-count', 'name')
	for item in results:
		if item['count'] >= 3:
			
			obj = {
				'name': item[fieldname],
				'count': item['count'],
				'creator': item['creator'],
				
				'default':None,
				
				'city':None,
				'region': None,
				'country': None,
			}
			
			data.append(obj)
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_rename(request):
	
	results = Mission.objects.filter(ref__in=request.data['refs'])
	for item in results:
		
		item.name = request.data['new_name']
		item.save()
		
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_delete(request):

	potential = Potential.objects.filter(title=request.data['title'], city__name=request.data['city_name'], country__name=request.data['country_name'])
	if potential.count() > 0:
		potential[0].delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_delete_title(request):

	potential = Potential.objects.filter(title=request.data['title'])
	if potential.count() > 0:
		potential[0].delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_exclude(request):
	
	results = Mission.objects.filter(mosaic__isnull=True, name=request.data['name'])
	for item in results:
		
		item.admin = False
		item.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def potential_validate(request):
	
	creator = None
	faction = None
	
	missions = Mission.objects.filter(ref__in=request.data['refs'])
	for item in missions:

		if not creator and not faction:
			creator = item.creator
			faction = item.faction

		item.name = request.data['title']
		item.validated = True
		item.save()
	
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
		
	potential = Potential(title=request.data['title'], count=missions.count(), city=city, country=country, creator=creator, faction=faction)
	potential.save()
	
	country_notifiers = Notif.objects.filter(country=country, region__isnull=True, city__isnull=True).values_list('user__email')
	region_notifiers = Notif.objects.filter(country=country, region=region, city__isnull=True).values_list('user__email')
	city_notifiers = Notif.objects.filter(country=country, region=region, city=city).values_list('user__email')
	
	receivers = []
	for item in country_notifiers: receivers.append(item[0])
	for item in region_notifiers: receivers.append(item[0])
	for item in city_notifiers: receivers.append(item[0])
	receivers = set(receivers)
	receivers = list(receivers)

	if len(receivers) > 0:
		
		msg_plain = render_to_string('new_potential.txt', { 'url':potential.title.replace(' ', '%20'), 'name':potential.title, 'count':potential.count, 'country':country.name, 'region':region.name, 'city':city.name })
		
		for receiver in receivers:
			send_mail(
				'[MIM] New Potential Detected',
		    	msg_plain,
		    	'admin@myingressmosaics.com',
		    	[receiver],
		    	fail_silently=False,
		    )

	return Response(None, status=status.HTTP_200_OK)






#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def country_getList(request):
	
	data = { 'countries': [], }
	
	results = Country.objects.all().order_by('name')
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
	
	results = Region.objects.filter(country__pk=request.data['country_id']).order_by('name')
	for item in results:
		data['regions'].append(item.serialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_create(request):
	
	country = Country.objects.get(pk=request.data['country_id'])
	
	item = Region(country=country, name=request.data['name'], locale=request.data['locale'])
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
	
	for item in City.objects.filter(region=src):
		item.region = dest
		item.save()

	src.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def region_delete(request):
	
	item = Region.objects.get(pk=request.data['id'])
	item.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_getListFromCountryRegion(request):
	
	data = { 'cities': [], }
	
	results = City.objects.filter(region__pk=request.data['region_id']).order_by('name')
	for item in results:
		data['cities'].append(item.serialize())
	
	return Response(data, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_create(request):
	
	region = Region.objects.get(pk=request.data['region_id'])
	
	item = City(region=region, name=request.data['name'], locale=request.data['locale'])
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
	
	for item in src.potentials.all():
		item.city = dest
		item.save()
	
	src.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_delete(request):
	
	item = City.objects.get(pk=request.data['id'])
	item.delete()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def city_teleport(request):
	
	region = Region.objects.get(pk=request.data['region_id'])
	
	city = City.objects.get(pk=request.data['city_id'])
	city.region = region
	city.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
@api_view(['POST'])
@permission_classes((AllowAny, ))
def telegram_updates(request):
	
	bot = telepot.Bot('539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0')
	
	response_url = 'https://api.telegram.org/bot539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0/sendMessage'
	response_txt = ''

	try:

		# Inline query
		if 'inline_query' in request.data:
			
			query_id = request.data['inline_query']['id']
			query_string = request.data['inline_query']['query']

			results = Mosaic.objects.filter(title__icontains=query_string)
			print(str(results.count()))
			
			articles = []
			
			if results.count() > 0:
				for item in results:
				
					article = InlineQueryResultArticle(
							id=item.ref,
							title=item.title,
							input_message_content=InputTextMessageContent(
								message_text=item.title
							)
						)
					articles.append(article)
				
			response = bot.answerInlineQuery(query_id, articles)

			return Response(None, status=status.HTTP_200_OK)
			
		# City command
		elif '/city ' in request.data['message']['text']:
			city_query = request.data['message']['text'].replace('/city ', '')
			results = City.objects.filter(name__iexact=city_query)
			if results.count() > 0:
				city_data = results[0]
				response_txt += '<b>' + city_data.name + ', ' + city_data.region.name + ', ' + city_data.region.country.name + '</b>\r\n'
				response_txt += str(city_data.mosaics.all().count()) + ' mosaics\r\n'
				response_txt += '<a href="https://www.myingressmosaics.com/world/' + city_data.region.country.name + '/' + city_data.region.name + '/' + city_data.name + '">MIM link</a>'
			else:
				response_txt = 'No city found (' + city_query + ')'
		
		# Mosaic command
		elif '/mosaic ' in request.data['message']['text']:
			response_txt = 'mosaic command'
		
		# Creator command
		elif '/creator ' in request.data['message']['text']:
			response_txt = 'creator command'
		
		# Unknown command
		else:
			response_txt = 'Unknown command... sorry.'
		
		# Send response
		params = {
			'chat_id': request.data['message']['chat']['id'],
			'text': response_txt,
			'parse_mode': 'HTML',
			'disable_web_page_preview': True,
		}
		
		print(response_txt)
		response = requests.post(response_url, data=params)
		print(response)
	
	except Exception as e:
		print('%s (%s)' % (e.message, type(e)))
	
	return Response(None, status=status.HTTP_200_OK)
