#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token

from rest_social_auth.serializers import UserTokenSerializer

from .models import *

from django.http import HttpResponse

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
			
			order = 1
			
			for item in obj[9]:
				
				if item[5][0] == 'f':
				
					portal = Portal(mission=mission, lat=(item[5][1]/1000000.0), lng=(item[5][2]/1000000.0), order=order, title=item[2])
					portal.save()
					
				else:
				
					portal = Portal(mission=mission, lat=(item[5][2]/1000000.0), lng=(item[5][3]/1000000.0), order=order, title=item[2])
					portal.save()
				
				order += 1
		
			mission.computeInternalData()
		
		return Response(None, status=status.HTTP_200_OK)



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
	
	permission_classes = IsAuthenticated, 
    
	def view(self, request):
		
		data = {'team':request.user.profile.team, 'level':request.user.profile.level, 'name':request.user.username}
		
		return Response(data, status=status.HTTP_200_OK)



	def name(self, request):
		
		request.user.username = request.data['name']
		request.user.save()
		
		return Response(None, status=status.HTTP_200_OK)



	def missions(self, request):
		
		missions = None
		
		results = Mission.objects.filter(registerer=request.user.username)
		if results.count() > 0:
			
			missions = []
			for item in results:
				
				temp = {'name':item.title, 'creator':item.creator, 'faction':item.faction}
				missions.append(temp)
		
		return Response(missions, status=status.HTTP_200_OK)
