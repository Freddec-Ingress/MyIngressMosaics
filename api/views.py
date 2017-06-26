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
		jsonObject = json.dumps(dict(request.data))
		
		item = Mission(ref=jsonObject[0], data=request.data)
		item.save()
		
		return Response(None, status=status.HTTP_200_OK)
