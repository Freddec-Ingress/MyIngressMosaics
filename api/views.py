#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import *



#---------------------------------------------------------------------------------------------------
class ExtensionViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
    
    
	def check(self, request):
		
		import json
		obj = json.loads(request.body)
		
		data = []
		
		for item in obj[0]:
			temp = {'mid':item[0], 'status': 'notregistered'}
			data.append(temp)
		
		from django.http import JsonResponse
		return JsonResponse(data)
    
    
    
	def register(self, request):

		import json
		obj = json.loads(request.body)
		
		results = Mission.objects.filter(ref=obj[0])
		if (results.count() < 1):
			
			mission = Mission(ref=obj[0], title=obj[1], desc=obj[2], creator=obj[3], faction=obj[4], image=obj[10],
							  data=request.body)
			mission.save()
			
			order = 1
			
			for item in obj[9]:
				
				portal = Portal(mission=mission, lat=(item[5][2]/1000000), lng=(item[5][3]/1000000), order=order, title=item[2])
				portal.save()
				
				order += 1
		
			mission.computeInternalData()
		
		return Response(None, status=status.HTTP_200_OK)
