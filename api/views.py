#!/usr/bin/env python
# coding: utf-8

import json

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token

from rest_social_auth.serializers import UserTokenSerializer

from .models import *

from django.http import HttpResponse

from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model, authenticate, logout



#---------------------------------------------------------------------------------------------------
@csrf_exempt
def ext_check(request):
	
	data = []
	
	import json
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
class ExtensionViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
	def register(self, request):

		import json
		obj = json.loads(request.body)
		
		mission = None
		
		results = Mission.objects.filter(ref=obj[0])
		if (results.count() < 1):
			
			mission = Mission(ref=obj[0], title=obj[1], desc=obj[2], creator=obj[3], faction=obj[4], image=obj[10], registerer=obj[11],
							  data=request.body)
			mission.save()
			
		else:
			
			mission = results[0]
			
			mission.ref = obj[0]
			mission.title = obj[1]
			mission.desc = obj[2]
			mission.creator = obj[3]
			mission.faction = obj[4]
			mission.image = obj[10]
			mission.register = obj[11]
			mission.data = request.body
			
			mission.save()
			
		order = 1
		
		for item in obj[9]:
			
			if not item[5]:
			
				portal = Portal(mission=mission, lat=0.0, lng=0.0, order=order, title='Unavailable')
				portal.save()
				
			elif item[5][0] == 'f':
			
				portal = Portal(mission=mission, lat=(item[5][1]/1000000.0), lng=(item[5][2]/1000000.0), order=order, title=item[2])
				portal.save()
				
			else:
			
				portal = Portal(mission=mission, lat=(item[5][2]/1000000.0), lng=(item[5][3]/1000000.0), order=order, title=item[2])
				portal.save()
			
			order += 1
	
		mission.computeInternalData()
		
		return Response('Registered', status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
class AccountViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
	def login(self, request):
		
		user = authenticate(username=request.data['username'], password=request.data['password'])
		if user is None:
			return Response('error_USER_UNKNOWN', status=status.HTTP_400_BAD_REQUEST)
		
		return Response(UserTokenSerializer(user).data, status=status.HTTP_200_OK)



	def register(self, request):
		
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



	def logout(self, request):
		
		logout(request)
		
		return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
class ProfileViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
	def view(self, request):
		
		if (request.user.is_authenticated):
		
			data = {
				'team': request.user.profile.team,
				'level': request.user.profile.level,
				'name': request.user.username,
				'superuser': request.user.is_superuser,
			}
		
		else:
			data = None
		
		return Response(data, status=status.HTTP_200_OK)



	def name(self, request):
		
		request.user.username = request.data['name']
		request.user.save()
		
		return Response(None, status=status.HTTP_200_OK)



	def missions(self, request):
		
		missions = None
		
		results = Mission.objects.filter(registerer=request.user.username, mosaic__isnull = True).order_by('title')
		if results.count() > 0:
			
			missions = []
			for item in results:
				
				temp = {'ref':item.ref, 'name':item.title, 'desc':item.desc, 'creator':item.creator, 'faction':item.faction, 'image':item.image, 'order':item.order,
					'lat':item._startLat, 'lng':item._startLng,
				}
				
				missions.append(temp)
		
		return Response(missions, status=status.HTTP_200_OK)



	def mosaics(self, request):
		
		mosaics = None
		
		results = Mosaic.objects.filter(registerer=request.user).order_by('title')
		if results.count() > 0:
			
			mosaics = []
			for item in results:
				
				temp = {'ref':item.ref, 'name':item.title}
				mosaics.append(temp)
		
		return Response(mosaics, status=status.HTTP_200_OK)


    
	def create(self, request):
		
		mosaic = Mosaic(	registerer = request.user,
							cols = int(request.data['cols']),
							type = request.data['type'],
							desc = request.data['desc'],
							city = request.data['city'],
							rows = int(request.data['rows']),
							title = request.data['title'],
							region = request.data['region'],
							country = request.data['country']
						)
		mosaic.save()
		
		for m in request.data['missions']:
			
			result = Mission.objects.filter(ref=m['ref'])
			if result.count() > 0:
				
				item = result[0]
				item.mosaic = mosaic
				item.order = m['order']
				item.save()
		
		mosaic.computeInternalData()
		
		return Response(mosaic.ref, status=status.HTTP_200_OK)
		
		
		
	def deleteMission(self, request):
		
		result = Mission.objects.filter(ref=request.data['ref'])
		if result.count() > 0:
			result[0].delete();
			
		return Response(None, status=status.HTTP_200_OK)
		
	
	
#---------------------------------------------------------------------------------------------------
class MosaicViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
	def view(self, request, ref):
		
		data = None
		
		result = Mosaic.objects.filter(ref=ref)
		if result.count() > 0:
			
			mosaic = result[0]
			mosaic.computeDistance()
			data = mosaic.serialize()
		
		return Response(data, status=status.HTTP_200_OK)



	def edit(self, request):
		
		if request.user.is_superuser:
			result = Mosaic.objects.filter(ref=request.data['ref'])
		else:
			result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
		
		if result.count() > 0:
			mosaic = result[0]
			
			mosaic.city = request.data['city']
			mosaic.desc = request.data['desc']
			mosaic.type = request.data['type']
			mosaic.cols = request.data['cols']
			mosaic.rows = request.data['rows']
			mosaic.title = request.data['title']
			mosaic.region = request.data['region']
			mosaic.country = request.data['country']
			
			mosaic.save()
		
			data = mosaic.serialize()
			return Response(data, status=status.HTTP_200_OK)
			
		return Response(None, status=status.HTTP_404_NOT_FOUND)



	def reorder(self, request):

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
			
			data = mosaic.serialize()
			return Response(data, status=status.HTTP_200_OK)

		return Response(None, status=status.HTTP_404_NOT_FOUND)



	def delete(self, request):
		
		if request.user.is_superuser:
			result = Mosaic.objects.filter(ref=request.data['ref'])
		else:
			result = Mosaic.objects.filter(ref=request.data['ref'], registerer=request.user)
		
		if result.count() > 0:
			
			mosaic = result[0]
			mosaic.delete()
		
		return Response(None, status=status.HTTP_200_OK)



	def remove(self, request):
		
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
				
				data = mosaic.serialize()
				return Response(data, status=status.HTTP_200_OK)
		
		return Response(None, status=status.HTTP_404_NOT_FOUND)



	def add(self, request):
		
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
				
				mosaic.computeInternalData()
				mosaic.save()
				
				data = mosaic.serialize()
				return Response(data, status=status.HTTP_200_OK)
		
		return Response(None, status=status.HTTP_404_NOT_FOUND)



	def potential(self, request):
		
		result = Mosaic.objects.filter(ref=request.data['ref'])
		if result.count() > 0:
			
			mosaic = result[0]
			
			creators = mosaic.creators.all().values_list('name', flat=True)
			
			missions = []
				
			results = Mission.objects.filter(mosaic__isnull=True).filter(Q(title__contains=mosaic.title) | Q(creator__in=creators))
			if results.count() > 0:
				
				for item in results:
					
					temp = {'ref':item.ref, 'name':item.title, 'desc':item.desc, 'creator':item.creator, 'faction':item.faction, 'image':item.image, 'order':item.order,
						'lat':item._startLat, 'lng':item._startLng,
					}
					
					missions.append(temp)
			
			return Response(missions, status=status.HTTP_200_OK)
			
		return Response(None, status=status.HTTP_404_NOT_FOUND)



	def repair(self, request):
		
		if not request.user.is_superuser:
			return Response(data, status=status.HTTP_403_FORBIDDEN)
			
		result = Mosaic.objects.filter(ref=request.data['ref'])
		if result.count() > 0:
			
			mosaic = result[0]
			
			for m in mosaic.missions.all():
				m.computeInternalData()
			
			mosaic.computeDistance()
			
		return Response(None, status=status.HTTP_200_OK)



	def latest(self, request):
			
		results = Mosaic.objects.order_by('-pk')[:12]
		if results.count() > 0:
			
			data = []
			
			for item in results:
				
				mosaic = item.homeSerialize()
				data.append(mosaic)
			
			return Response(data, status=status.HTTP_200_OK)
			
		return Response(None, status=status.HTTP_404_NOT_FOUND)



#---------------------------------------------------------------------------------------------------
class DataViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
    
    
	def world(self, request):
		
		data = None
		
		results = Mosaic.objects.values('country').distinct()
		if (results.count() > 0):
			
			data = []
			
			for item in results:
				
				country = {
					'mosaics': Mosaic.objects.filter(country=item['country']).count(),
					'name': item['country'],
				}
				
				data.append(country)
		
		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def country(self, request):
		
		data = None
		
		results = Mosaic.objects.filter(country=request.data['country']).values('region').distinct()
		if (results.count() > 0):
			
			data = []
			
			for item in results:
				
				region = {
					'mosaics': Mosaic.objects.filter(country=request.data['country'], region=item['region']).count(),
					'name': item['region'],
				}
				
				if region['name'] == '':
					region['name'] = 'Not specified'
				
				data.append(region)

		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def renameCountry(self, request):
		
		if not request.user.is_superuser:
			return Response(data, status=status.HTTP_403_FORBIDDEN)
		
		results = Mosaic.objects.filter(country=request.data['oldValue'])
		if (results.count() > 0):
			
			for item in results:
				
				item.country = request.data['newValue']
				item.save()

		return Response(None, status=status.HTTP_200_OK)
		
	
	
	def region(self, request):
		
		data = None
		
		if request.data['region'] == 'Not specified':
			request.data['region'] = ''
		
		results = Mosaic.objects.filter(country=request.data['country'], region=request.data['region']).values('city').distinct()
		if (results.count() > 0):
			
			data = []
			
			for item in results:
				
				city = {
					'mosaics': Mosaic.objects.filter(country=request.data['country'], region=request.data['region'], city=item['city']).count(),
					'name': item['city'],
				}
			
				data.append(city)
			
		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def setRegion(self, request):
		
		if not request.user.is_superuser:
			return Response(data, status=status.HTTP_403_FORBIDDEN)

		results = Mosaic.objects.filter(city=request.data['city'])
		if (results.count() > 0):
			
			for item in results:
				
				item.region = request.data['region']
				item.save()

		return Response(None, status=status.HTTP_200_OK)
    
    
    
	def renameCity(self, request):
		
		if not request.user.is_superuser:
			return Response(data, status=status.HTTP_403_FORBIDDEN)
		
		results = Mosaic.objects.filter(city=request.data['oldValue'])
		if (results.count() > 0):
			
			for item in results:
				
				item.city = request.data['newValue']
				item.save()

		return Response(None, status=status.HTTP_200_OK)
    
    
    
	def city(self, request):
		
		data = None
		
		if request.data['region'] == 'Not specified':
			request.data['region'] = ''
		
		results = Mosaic.objects.filter(country=request.data['country'], region=request.data['region'], city=request.data['city'])
		if (results.count() > 0):
			
			data = []
			
			for item in results:
				
				mosaic = item.minSerialize()
				data.append(mosaic)
		
		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def creator(self, request):
		
		data = None
		
		results = Creator.objects.filter(name=request.data['creator'])
		if (results.count() > 0):
			
			creator = results[0]
			
			data = {
				'faction': creator.faction,
				'mosaics': [],
			}
			
			for item in creator.mosaic_set.all():
				
				mosaic = item.serialize()
				data['mosaics'].append(mosaic)
		
		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def search(self, request):
		
		data = {
			'countries': None,
			'regions': None,
			'cities': None,
			'creators': None,
			'mosaics': None,
		}
		
		results = Mosaic.objects.filter(country__icontains=request.data['text']).values('country').distinct()
		if (results.count() > 0):
			
			data['countries'] = []
			
			for item in results:
				
				country = {
					'name': item['country'],
				}
				
				data['countries'].append(country)
		
		results = Mosaic.objects.filter(region__icontains=request.data['text']).values('country', 'region').distinct()
		if (results.count() > 0):
			
			data['regions'] = []
			
			for item in results:
				
				region = {
					'country': item['country'],
					'name': item['region'],
				}
				
				data['regions'].append(region)
		
		results = Mosaic.objects.filter(city__icontains=request.data['text']).values('country', 'region', 'city').distinct()
		if (results.count() > 0):
			
			data['cities'] = []
			
			for item in results:
				
				city = {
					'country': item['country'],
					'region': item['region'],
					'name': item['city'],
				}
				
				data['cities'].append(city)
		
		results = Creator.objects.filter(name__icontains=request.data['text'])
		if (results.count() > 0):
			
			data['creators'] = []
			
			for item in results:
				
				creator = {
					'name': item.name,
					'faction': item.faction,
				}
				
				data['creators'].append(creator)
		
		results = Mosaic.objects.filter(title__icontains=request.data['text'])
		if (results.count() > 0):
			
			data['mosaics'] = []
			
			for item in results:
				
				mosaic = item.serialize()
				data['mosaics'].append(mosaic)
		
		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def map(self, request):
		
		data = None
		
		results = Mosaic.objects.filter(_startLat__gte=request.data['sLat'], _startLng__gte=request.data['sLng']).filter(_startLat__lte=request.data['nLat'], _startLng__lte=request.data['nLng'])
		if (results.count() > 0):
			
			data = []
			
			for item in results:
				
				mosaic = item.mapSerialize()
				data.append(mosaic)

		return Response(data, status=status.HTTP_200_OK)
    
    
    
	def details(self, request):
		
		data = None
		
		results = Mosaic.objects.filter(ref=request.data['ref'])
		if (results.count() > 0):
			
			data = []
			
			item = results[0]
			
			mosaic = item.serialize()
			data.append(mosaic)

		return Response(data, status=status.HTTP_200_OK)
