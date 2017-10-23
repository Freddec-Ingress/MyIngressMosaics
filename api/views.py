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
	
	currentArray.append({'name':'Look around Weymouth', 'link':'/mosaic/15282', 'city':' Weymouth'});
	currentArray.append({'name':'Double Vision', 'link':'/mosaic/21213', 'city':' Worcester'});
	currentArray.append({'name':'Beacon Street Hackapalooza', 'link':'/mosaic/21293', 'city':' Brookline'});
	currentArray.append({'name':'Historic Bedford', 'link':'/mosaic/23694', 'city':' Bedford'});
	currentArray.append({'name':'Shelburn Falls', 'link':'/mosaic/22647', 'city':' Shelburne Falls'});
	currentArray.append({'name':'La Salette Shrine', 'link':'/mosaic/1665', 'city':' Attleboro'});
	currentArray.append({'name':'Marblehead Banner', 'link':'/mosaic/2214', 'city':' Marblehead'});
	currentArray.append({'name':'Central Square', 'link':'/mosaic/5886', 'city':' Cambridge'});
	currentArray.append({'name':'Williams', 'link':'/mosaic/5896', 'city':' Williamstown'});
	currentArray.append({'name':'The Chain Bridge', 'link':'/mosaic/7217', 'city':' Amesbury'});
	currentArray.append({'name':'Battle Road Trail', 'link':'/mosaic/7848', 'city':' Concord'});
	currentArray.append({'name':'Harvard University', 'link':'/mosaic/9181', 'city':' Cambridge'});
	currentArray.append({'name':'Where s Waldo in the USA', 'link':'/mosaic/11195', 'city':' Salem'});
	currentArray.append({'name':'Northeastern University', 'link':'/mosaic/11234', 'city':' Boston'});
	currentArray.append({'name':'Witch City Kitty Committee', 'link':'/mosaic/11627', 'city':' Salem'});
	currentArray.append({'name':'Colleges of the Fenway', 'link':'/mosaic/14035', 'city':' ROXBURY CROSSING'});
	currentArray.append({'name':'North Attleboro', 'link':'/mosaic/14449', 'city':' North Attleborough'});
	currentArray.append({'name':'Historic Maynard', 'link':'/mosaic/16990', 'city':' Maynard'});
	currentArray.append({'name':'Babson College', 'link':'/mosaic/17540', 'city':' Wellesley'});
	currentArray.append({'name':'RESIST in Milford  MA', 'link':'/mosaic/19554', 'city':' Milford'});
	currentArray.append({'name':'#MissionsForGood LGBT Awarness #BAGLY', 'link':'/mosaic/21155', 'city':' Boston'});
	currentArray.append({'name':'The Town of Easthampton MA', 'link':'/mosaic/21593', 'city':' Easthampton'});
	currentArray.append({'name':'Bro  Boston Edition', 'link':'/mosaic/22309', 'city':' Boston'});
	currentArray.append({'name':'#Magnus Reawakens  Heartbeat - Boston', 'link':'/mosaic/22489', 'city':' Boston'});
	currentArray.append({'name':'Amherst  Massachusetts', 'link':'/mosaic/23283', 'city':' Amherst'});
	currentArray.append({'name':'Shelburne Falls  Massachusetts', 'link':'/mosaic/23330', 'city':' Shelburne Falls'});
	currentArray.append({'name':'Turners Falls  Massachusetts', 'link':'/mosaic/23336', 'city':' Montague'});
	currentArray.append({'name':'Cape Cod Whale Trail', 'link':'/mosaic/25415', 'city':' Provincetown'});
	currentArray.append({'name':'Deerfield  Massachusetts', 'link':'/mosaic/25419', 'city':' Deerfield'});
	currentArray.append({'name':'Over the River and Through the Wood', 'link':'/mosaic/27517', 'city':' Medford'});
	currentArray.append({'name':'Wellesley College', 'link':'/mosaic/28011', 'city':' Wellesley'});
	currentArray.append({'name':'Boston Red Sox', 'link':'/mosaic/2004', 'city':' Boston'});
	currentArray.append({'name':'Boston Pride', 'link':'/mosaic/2109', 'city':' Boston'});
	currentArray.append({'name':'Mystic River', 'link':'/mosaic/2865', 'city':' Winchester'});
	currentArray.append({'name':'Neighborhoods of Fall River', 'link':'/mosaic/8455', 'city':' Fall River'});
	currentArray.append({'name':'Grafton Graffiti', 'link':'/mosaic/12152', 'city':' Grafton'});
	currentArray.append({'name':'MBTA Blue Line', 'link':'/mosaic/12160', 'city':' Revere'});
	currentArray.append({'name':'Uxbridge Understanding', 'link':'/mosaic/12484', 'city':' Uxbridge'});
	currentArray.append({'name':'Historic Northbridge', 'link':'/mosaic/12815', 'city':' Uxbridge'});
	currentArray.append({'name':'Always Remember', 'link':'/mosaic/13673', 'city':' Boston'});
	currentArray.append({'name':'Attleboro', 'link':'/mosaic/14448', 'city':' Attleboro'});
	currentArray.append({'name':'Harry Potter Seie', 'link':'/mosaic/15259', 'city':' Salem'});
	currentArray.append({'name':'Boston Waterfront', 'link':'/mosaic/19095', 'city':' Boston'});
	currentArray.append({'name':'How To Be A Panda (Boston)', 'link':'/mosaic/21153', 'city':' Boston'});
	currentArray.append({'name':'Mmm    Donuts', 'link':'/mosaic/21154', 'city':' Cambridge'});
	currentArray.append({'name':'Boston Harbor', 'link':'/mosaic/23361', 'city':' Boston'});
	currentArray.append({'name':'Jaws Tisbury', 'link':'/mosaic/25481', 'city':' Tisbury'});
	currentArray.append({'name':'KBOS Logan International', 'link':'/mosaic/25756', 'city':' Boston'});
	currentArray.append({'name':'Pittsfield Hayday', 'link':'/mosaic/26130', 'city':' Pittsfield'});
	currentArray.append({'name':'Midnight in Salem', 'link':'/mosaic/9562', 'city':' Salem'});
	currentArray.append({'name':'Mass Bay Transit - Red Line', 'link':'/mosaic/10045', 'city':' Cambridge'});
	currentArray.append({'name':'Sello de Worcester', 'link':'/mosaic/11353', 'city':' Worcester'});
	currentArray.append({'name':'波士顿唐人街   Boston s Chinatown', 'link':'/mosaic/12084', 'city':' Boston'});
	currentArray.append({'name':'Boston Harborwalk', 'link':'/mosaic/12194', 'city':' Boston'});
	currentArray.append({'name':'Lower Allston', 'link':'/mosaic/12227', 'city':' Boston'});
	currentArray.append({'name':'Worcester History', 'link':'/mosaic/15779', 'city':' Worcester'});
	currentArray.append({'name':'MBTA Orange Line', 'link':'/mosaic/16762', 'city':' Boston'});
	currentArray.append({'name':'The Boston Massacre', 'link':'/mosaic/16905', 'city':' Boston'});
	currentArray.append({'name':'The Esplanade', 'link':'/mosaic/17044', 'city':' Boston'});
	currentArray.append({'name':'#MissionsForGood Boston Edition', 'link':'/mosaic/17205', 'city':' Boston'});
	currentArray.append({'name':'Boston Tea Party', 'link':'/mosaic/17692', 'city':' Boston'});
	currentArray.append({'name':'Greetings from Cambridge', 'link':'/mosaic/17695', 'city':' Cambridge'});
	currentArray.append({'name':'Boston Skyline v2', 'link':'/mosaic/17696', 'city':' Boston'});
	currentArray.append({'name':'Visit the Pru', 'link':'/mosaic/17788', 'city':' Boston'});
	currentArray.append({'name':'#MissionsForGood The Greenway', 'link':'/mosaic/19074', 'city':' Boston'});
	currentArray.append({'name':'Visit Cambridge', 'link':'/mosaic/19631', 'city':' Cambridge'});
	currentArray.append({'name':'Visit Beautiful Arlington', 'link':'/mosaic/20141', 'city':' Arlington'});
	currentArray.append({'name':'Wachusett Reservoir', 'link':'/mosaic/21214', 'city':' Lancaster'});
	currentArray.append({'name':'Greetings from Allston', 'link':'/mosaic/21498', 'city':' Boston'});
	currentArray.append({'name':'The Quest for Ice Cream', 'link':'/mosaic/22169', 'city':' Boston'});
	currentArray.append({'name':'Founding Fathers - Ben Franklin', 'link':'/mosaic/22483', 'city':' Boston'});
	currentArray.append({'name':'Make Way for Ducklings', 'link':'/mosaic/22829', 'city':' Boston'});
	currentArray.append({'name':'Jump Portals with Evel', 'link':'/mosaic/23380', 'city':' Worcester'});
	currentArray.append({'name':'Outer Cape', 'link':'/mosaic/23421', 'city':' Eastham'});
	currentArray.append({'name':'Kenneth F  Burns Bridge', 'link':'/mosaic/23678', 'city':' Worcester'});
	currentArray.append({'name':'Link Amp Kitten Camberville', 'link':'/mosaic/24455', 'city':' Cambridge'});
	currentArray.append({'name':'Cradles to Crayons', 'link':'/mosaic/24953', 'city':' Boston'});
	currentArray.append({'name':'Boston Symphony Orchestra', 'link':'/mosaic/25526', 'city':' Boston'});
	currentArray.append({'name':'The Listener - Boston', 'link':'/mosaic/25602', 'city':' Boston'});
	currentArray.append({'name':'Wandering Westfield', 'link':'/mosaic/26854', 'city':' Westfield'});
	currentArray.append({'name':'MIT Puzzle Mosaic x of y', 'link':'/mosaic/24801', 'city':' Cambridge'});
	currentArray.append({'name':'Public Garden and Environs', 'link':'/mosaic/4234', 'city':' Boston'});
	currentArray.append({'name':'Boston Brownstones', 'link':'/mosaic/16722', 'city':' Boston'});
	currentArray.append({'name':'Boston Cambridge Walking Tour', 'link':'/mosaic/16906', 'city':' Boston'});
	currentArray.append({'name':'Brookline Massachusetts', 'link':'/mosaic/16907', 'city':' Brookline'});
	currentArray.append({'name':'UMass Amherst  The Full Tour', 'link':'/mosaic/16991', 'city':' Amherst'});
	currentArray.append({'name':'Massachusetts State House', 'link':'/mosaic/21499', 'city':' Boston'});
	currentArray.append({'name':'Wally the Green Monster', 'link':'/mosaic/21970', 'city':' Boston'});
	currentArray.append({'name':'City of Homes', 'link':'/mosaic/23768', 'city':' Springfield'});
	currentArray.append({'name':'Boston New Horizons', 'link':'/mosaic/24165', 'city':' Cambridge'});
	currentArray.append({'name':'Go Sox', 'link':'/mosaic/24815', 'city':' Boston'});
	currentArray.append({'name':'Acorn Street', 'link':'/mosaic/24997', 'city':' Boston'});
	currentArray.append({'name':'Salem Witch Trials', 'link':'/mosaic/25300', 'city':' Salem'});
	currentArray.append({'name':'Friendship of Salem', 'link':'/mosaic/25768', 'city':' Salem'});
	currentArray.append({'name':'Viva la Resistance', 'link':'/mosaic/2112', 'city':' Cambridge'});
	currentArray.append({'name':'Freedom Trail', 'link':'/mosaic/16763', 'city':' Boston'});
	currentArray.append({'name':'Citgo Boston', 'link':'/mosaic/2111', 'city':' Boston'});
	currentArray.append({'name':'Boston - Don t Look Back', 'link':'/mosaic/2824', 'city':' Cambridge'});
	currentArray.append({'name':'Call me Ishmael', 'link':'/mosaic/26674', 'city':' New Bedford'});
	currentArray.append({'name':'Go Exploring', 'link':'/mosaic/2320', 'city':' Hingham'});
	currentArray.append({'name':'I ll get you my pretty', 'link':'/mosaic/18151', 'city':' Boston'});
	currentArray.append({'name':'#Magnus Reawakens  Boston Xfac Edition', 'link':'/mosaic/21829', 'city':' Boston'});
	currentArray.append({'name':'MBTA Green Line', 'link':'/mosaic/5838', 'city':' Cambridge'});
	currentArray.append({'name':'Zakim Banner', 'link':'/mosaic/3755', 'city':' Boston'});
	currentArray.append({'name':'Welcome to Mordor (Blackstone Valley)', 'link':'/mosaic/23671', 'city':' Worcester'});
	currentArray.append({'name':'John Hancock Tower', 'link':'/mosaic/23752', 'city':' Boston'});
	currentArray.append({'name':'Welcome to Boston', 'link':'/mosaic/21834', 'city':' Boston'});

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
