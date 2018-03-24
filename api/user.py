#!/usr/bin/env python
# coding: utf-8

import urllib
import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from .models import *



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
			
	user = authenticate(username=name, password='password')
	login(request, user)
	
	token, created = Token.objects.get_or_create(user=user)

	return Response({ 'data': { 'token':token.key, }}, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_logout(request):
	
	logout(request)
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def user_edit(request):
	
	request.user.profile.faction = request.data['faction']
	request.user.profile.save()
	
	return Response(None, status=status.HTTP_200_OK)
