#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def link_create(request):
	
	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])

	results = mosaic_obj.links.filter(user=request.user, type=request.data['type'])
	if results.count() < 1:
		
		link_obj = Link(mosaic=mosaic, user=request.user, type=request.data['type'])
		link_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def link_delete(request):
	
	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])
		
	results = mosaic.links.filter(user=request.user, type=request.data['type'])
	if results.count() > 0:
		
		link_obj = result[0]
		link_obj.delete()
	
	return Response(None, status=status.HTTP_200_OK)
