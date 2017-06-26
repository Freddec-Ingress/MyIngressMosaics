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
		
		item = Mission(	ref=obj[0],
						title=obj[0],
						desc=obj[0],
						creator=obj[0],
						faction=obj[0],
						image=obj[0],
						data=request.body,
			)
		item.save()
		
		return Response(None, status=status.HTTP_200_OK)
