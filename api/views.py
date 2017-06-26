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
		return Response(None, status=status.HTTP_200_OK)
    
    
    
	def register(self, request):

		import json
		obj = json.loads(request.body)
		
		mission = Mission(ref=obj[0], title=obj[1], desc=obj[2], creator=obj[3], faction=obj[4], image=obj[10],
						  data=request.body)
		mission.save()
		
		order = 0
		
		for item in obj[9]:
			
			portal = Portal(mission=mission, lat=item[5][2], lng=item[5][3], order=order, title=item[2],
							data=''.join(item))
			portal.save()
			
			order += 1
		
		return Response(None, status=status.HTTP_200_OK)
