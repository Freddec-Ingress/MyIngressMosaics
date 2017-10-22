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
	
	currentArray.append({'name':'Indianapolis Airport', 'link':'/mosaic/13843', 'city':' Indianapolis'});
	currentArray.append({'name':'Welcome To  The Well', 'link':'/mosaic/18938', 'city':' Carmel'});
	currentArray.append({'name':'Near West Side Historic District', 'link':'/mosaic/19669', 'city':' Bloomington'});	
	currentArray.append({'name':'NIBCO', 'link':'/mosaic/19321', 'city':' Elkhart'});
	currentArray.append({'name':'Elkhart Hopscotch', 'link':'/mosaic/21174', 'city':' Elkhart'});
	currentArray.append({'name':'Oakwood Cemetery', 'link':'/mosaic/387', 'city':' Warsaw'});
	currentArray.append({'name':'Farming Up', 'link':'/mosaic/3207', 'city':' Lafayette'});
	currentArray.append({'name':'Boiler Up', 'link':'/mosaic/5791', 'city':' West Lafayette'});
	currentArray.append({'name':'Monument Mission', 'link':'/mosaic/5798', 'city':' Indianapolis'});
	currentArray.append({'name':'HEBRON HACK BANNER', 'link':'/mosaic/9185', 'city':' Hebron'});
	currentArray.append({'name':'Chapel Lawn Cemetery Rainbow', 'link':'/mosaic/9675', 'city':' Crown Point'});
	currentArray.append({'name':'The Fort Wayne Factions Welcome You', 'link':'/mosaic/12334', 'city':' Fort Wayne'});
	currentArray.append({'name':'Series at the Lake County Fairgrounds', 'link':'/mosaic/14100', 'city':' Crown Point'});
	currentArray.append({'name':'Faith in Vigo County', 'link':'/mosaic/16100', 'city':' Terre Haute'});
	currentArray.append({'name':'Syracuse  Indiana banner', 'link':'/mosaic/18362', 'city':' Syracuse'});
	currentArray.append({'name':'Emerson Heights Field Trips', 'link':'/mosaic/20450', 'city':' Indianapolis'});
	currentArray.append({'name':'Peace at Lake George', 'link':'/mosaic/23012', 'city':' Hobart'});
	currentArray.append({'name':'Biohazard Edinburgh', 'link':'/mosaic/23280', 'city':' Edinburgh'});
	currentArray.append({'name':'Hike Around Coffee Creek', 'link':'/mosaic/24948', 'city':' Chesterton'});
	currentArray.append({'name':'Fort Wayne Letter Series', 'link':'/mosaic/10440', 'city':' Fort Wayne'});
	currentArray.append({'name':'Winona Village', 'link':'/mosaic/388', 'city':' Winona Lake'});
	currentArray.append({'name':'IUPUI', 'link':'/mosaic/5644', 'city':' Indianapolis'});
	currentArray.append({'name':'Edinburgh Fire  Rescue', 'link':'/mosaic/8691', 'city':' Edinburgh'});
	currentArray.append({'name':'Bedford', 'link':'/mosaic/8800', 'city':' Bedford'});
	currentArray.append({'name':'Wayne County', 'link':'/mosaic/11296', 'city':' Richmond'});
	currentArray.append({'name':'Headwaters Park', 'link':'/mosaic/12156', 'city':' Fort Wayne'});
	currentArray.append({'name':'Monon Trail', 'link':'/mosaic/12660', 'city':' Westfield'});
	currentArray.append({'name':'Westfield is the Bestfield', 'link':'/mosaic/12663', 'city':' Westfield'});
	currentArray.append({'name':'Spooky Crown Hill', 'link':'/mosaic/14965', 'city':' Indianapolis'});
	currentArray.append({'name':'#IngressFS  CrownHill', 'link':'/mosaic/14966', 'city':' Indianapolis'});
	currentArray.append({'name':'Gateway to the Future Arch', 'link':'/mosaic/15232', 'city':' West Lafayette'});
	currentArray.append({'name':'Falcons of Zionsville', 'link':'/mosaic/17098', 'city':' Zionsville'});
	currentArray.append({'name':'Rogue Fishers', 'link':'/mosaic/17099', 'city':' Fishers'});
	currentArray.append({'name':'Trolls in the Dungeon', 'link':'/mosaic/17100', 'city':' Indianapolis'});
	currentArray.append({'name':'Stars of Carmel', 'link':'/mosaic/17585', 'city':' Carmel'});
	currentArray.append({'name':'Noble Wind', 'link':'/mosaic/17864', 'city':' Noblesville'});
	currentArray.append({'name':'#IngressFS Franklin Indiana', 'link':'/mosaic/18180', 'city':' Franklin'});
	currentArray.append({'name':'Fort Wayne s Very Own', 'link':'/mosaic/18229', 'city':' Fort Wayne'});
	currentArray.append({'name':'Goshen Banner', 'link':'/mosaic/18548', 'city':' Goshen'});
	currentArray.append({'name':'#IngressFS Butler University', 'link':'/mosaic/18666', 'city':' Indianapolis'});
	currentArray.append({'name':'Blue Line of Westfield', 'link':'/mosaic/18667', 'city':' Westfield'});
	currentArray.append({'name':'#IngressFS April  Fools Rush', 'link':'/mosaic/20448', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum Red', 'link':'/mosaic/21150', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum Orange', 'link':'/mosaic/21151', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum Yellow', 'link':'/mosaic/21152', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum Green', 'link':'/mosaic/21160', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum Blue', 'link':'/mosaic/21161', 'city':' Alexandria'});
	currentArray.append({'name':'Color Spectrum Black', 'link':'/mosaic/21730', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum White', 'link':'/mosaic/21731', 'city':' Anderson'});
	currentArray.append({'name':'Color Spectrum Indigo', 'link':'/mosaic/21732', 'city':' Alexandria'});
	currentArray.append({'name':'Color Spectrum Violet', 'link':'/mosaic/21733', 'city':' Anderson'});
	currentArray.append({'name':'Crown Point Aerial Mosaic', 'link':'/mosaic/23022', 'city':' Crown Point'});
	currentArray.append({'name':'#IngressFS  Zionsville', 'link':'/mosaic/23100', 'city':' Zionsville'});
	currentArray.append({'name':'Horror Stories (Franklin  IN)', 'link':'/mosaic/23351', 'city':' Franklin'});
	currentArray.append({'name':'#IngressFS May IUPUI', 'link':'/mosaic/23736', 'city':' Indianapolis'});
	currentArray.append({'name':'#IngressFS July  IMA', 'link':'/mosaic/24702', 'city':' Indianapolis'});
	currentArray.append({'name':'Lighthouse at Night', 'link':'/mosaic/24789', 'city':' Michigan City'});
	currentArray.append({'name':'M3  Downtown TH and ISU', 'link':'/mosaic/26313', 'city':' Terre Haute'});
	currentArray.append({'name':'#IngressFS Sept  Fountain Square', 'link':'/mosaic/26633', 'city':' Indianapolis'});
	currentArray.append({'name':'#IngressFS August  ISM', 'link':'/mosaic/26634', 'city':' Indianapolis'});
	currentArray.append({'name':'MissionDay  Gen Con', 'link':'/mosaic/6495', 'city':' Indianapolis'});
	currentArray.append({'name':'Pool Ball Set', 'link':'/mosaic/19407', 'city':' Rensselaer'});
	currentArray.append({'name':'Fort Wayne Southeast', 'link':'/mosaic/251', 'city':' Fort Wayne'});
	currentArray.append({'name':'One Brick Higher  Banner', 'link':'/mosaic/1311', 'city':' West Lafayette'});
	currentArray.append({'name':'Crown Point Banner', 'link':'/mosaic/4298', 'city':' Crown Point'});
	currentArray.append({'name':'Indiana State Museum', 'link':'/mosaic/6945', 'city':' Indianapolis'});
	currentArray.append({'name':'Indy Skyline from Crown Hill', 'link':'/mosaic/12183', 'city':' Indianapolis'});
	currentArray.append({'name':'Indiana State House', 'link':'/mosaic/12217', 'city':' Indianapolis'});
	currentArray.append({'name':'Indiana Harbor Hack Series', 'link':'/mosaic/12495', 'city':' Hammond'});
	currentArray.append({'name':'Garland Brook Cemetery Mosaic', 'link':'/mosaic/12509', 'city':' Columbus'});
	currentArray.append({'name':'Skyline of Indianapolis', 'link':'/mosaic/12626', 'city':' Indianapolis'});
	currentArray.append({'name':'Indianapolis Zoo', 'link':'/mosaic/12678', 'city':' Indianapolis'});
	currentArray.append({'name':'Purdue Engineering Fountain', 'link':'/mosaic/13233', 'city':' West Lafayette'});
	currentArray.append({'name':'Courthouse Square', 'link':'/mosaic/13449', 'city':' Warsaw'});
	currentArray.append({'name':'Trekkin  Across Indy', 'link':'/mosaic/13495', 'city':' Indianapolis'});
	currentArray.append({'name':'Richmond  Indiana', 'link':'/mosaic/13655', 'city':' Richmond'});
	currentArray.append({'name':'Crown Hill Bridge', 'link':'/mosaic/14048', 'city':' Indianapolis'});
	currentArray.append({'name':'Fort Wayne Watercolor', 'link':'/mosaic/14425', 'city':' Fort Wayne'});
	currentArray.append({'name':'Downtown Anderson', 'link':'/mosaic/14818', 'city':' Anderson'});
	currentArray.append({'name':'Manchester University', 'link':'/mosaic/16105', 'city':' North Manchester'});
	currentArray.append({'name':'North of 96th', 'link':'/mosaic/16672', 'city':' Carmel'});
	currentArray.append({'name':'Amish country', 'link':'/mosaic/16675', 'city':' Fort Wayne'});
	currentArray.append({'name':'Fort Wayne Museum of Art Mosaic', 'link':'/mosaic/16831', 'city':' Fort Wayne'});
	currentArray.append({'name':'IPFW Mastodon', 'link':'/mosaic/17077', 'city':' Fort Wayne'});
	currentArray.append({'name':'Downtown Fort Wayne', 'link':'/mosaic/17080', 'city':' Fort Wayne'});
	currentArray.append({'name':'Lawrence Village at the Fort', 'link':'/mosaic/17091', 'city':' Indianapolis'});
	currentArray.append({'name':'See-See The Sights of CC', 'link':'/mosaic/21600', 'city':' Columbia City'});
	currentArray.append({'name':'Indy Reawakened', 'link':'/mosaic/22700', 'city':' Indianapolis'});
	currentArray.append({'name':'Kitty Cat On The Border Hack Series', 'link':'/mosaic/23021', 'city':' Munster'});
	currentArray.append({'name':'Otherworldly Sun', 'link':'/mosaic/23023', 'city':' Chesterton'});
	currentArray.append({'name':'The Ingress Turret', 'link':'/mosaic/23024', 'city':' Dyer'});
	currentArray.append({'name':'INDY CANAL WALK', 'link':'/mosaic/23416', 'city':' Indianapolis'});
	currentArray.append({'name':'Millennium Sundial Trek', 'link':'/mosaic/23423', 'city':' West Lafayette'});
	currentArray.append({'name':'Camp Atterbury', 'link':'/mosaic/23436', 'city':' Franklin'});
	currentArray.append({'name':'Ft Wayne FS', 'link':'/mosaic/23449', 'city':' Fort Wayne'});
	currentArray.append({'name':'Nickel Plate Road 765', 'link':'/mosaic/23463', 'city':' Wabash'});
	currentArray.append({'name':'The Dark Side of NWI', 'link':'/mosaic/24933', 'city':' Crown Point'});
	currentArray.append({'name':'Tranquil River', 'link':'/mosaic/25121', 'city':' Portage'});
	currentArray.append({'name':'Happy Michigan City', 'link':'/mosaic/25205', 'city':' Michigan City'});
	currentArray.append({'name':'Spartan', 'link':'/mosaic/25299', 'city':' Whiteland'});
	currentArray.append({'name':'Snoopy', 'link':'/mosaic/25591', 'city':' Mooresville'});
	currentArray.append({'name':'Tiffer gone Crazy', 'link':'/mosaic/25606', 'city':' Newburgh'});
	currentArray.append({'name':'Traitor Trooper', 'link':'/mosaic/25607', 'city':' Indianapolis'});
	currentArray.append({'name':'Oak Hill Zombie Hunt', 'link':'/mosaic/25825', 'city':' Evansville'});
	currentArray.append({'name':'Franklin  IN', 'link':'/mosaic/25879', 'city':' Franklin'});
	currentArray.append({'name':'Wutang', 'link':'/mosaic/26343', 'city':' Indianapolis'});
	currentArray.append({'name':'Drift Monticello', 'link':'/mosaic/26635', 'city':' Monticello'});
	currentArray.append({'name':'Vintage Northwest Indiana', 'link':'/mosaic/4299', 'city':' Schererville'});
	currentArray.append({'name':'18 and 12', 'link':'/mosaic/17162', 'city':' Indianapolis'});
	currentArray.append({'name':'Lil Bub', 'link':'/mosaic/17320', 'city':' Bloomington'});
	currentArray.append({'name':'The Word of Life', 'link':'/mosaic/18354', 'city':' Notre Dame'});
	currentArray.append({'name':'Ft  Wayne s Own Starlet', 'link':'/mosaic/19746', 'city':' Fort Wayne'});
	currentArray.append({'name':'RES-ENL', 'link':'/mosaic/20441', 'city':' Indianapolis'});
	currentArray.append({'name':'Eye Of ADA', 'link':'/mosaic/20444', 'city':' Decatur'});
	currentArray.append({'name':'You are Free', 'link':'/mosaic/22704', 'city':' Noblesville'});
	currentArray.append({'name':'Wolf Country', 'link':'/mosaic/25513', 'city':' Franklin'});
	currentArray.append({'name':'Tippecanoe County Courthouse', 'link':'/mosaic/25730', 'city':' West Lafayette'});
	currentArray.append({'name':'Happy days', 'link':'/mosaic/16921', 'city':' Indianapolis'});
	currentArray.append({'name':'Explore Downtown Columbus', 'link':'/mosaic/21680', 'city':' Columbus'});
	currentArray.append({'name':'Deeper', 'link':'/mosaic/23018', 'city':' Indianapolis'});
	currentArray.append({'name':'Nevermore Down 24', 'link':'/mosaic/21599', 'city':' Wabash County'});
	currentArray.append({'name':'Magnus Reawakens  Luminescent Heart Indy', 'link':'/mosaic/22402', 'city':' Indianapolis'});
	currentArray.append({'name':'Irvington is Dangerous Take This', 'link':'/mosaic/27959', 'city':' Indianapolis'});
	currentArray.append({'name':'Notre Dame Resistance', 'link':'/mosaic/10352', 'city':' Notre Dame'});
	currentArray.append({'name':'Emerald Castle', 'link':'/mosaic/22703', 'city':' Indianapolis'});
	currentArray.append({'name':'The Dark Lady', 'link':'/mosaic/25665', 'city':' Franklin'});

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
