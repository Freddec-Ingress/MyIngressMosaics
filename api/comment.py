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
def comment_create(request):
	
	mosaic_obj = Mosaic.objects.get(ref=request.data['ref'])

	comment_obj = Comment(user=request.user, mosaic=mosaic_obj, text=request.data['text'])
	comment_obj.save()

	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_update(request):
	
	comment_obj = Comment.objects.get(pk=request.data['id'])
	comment_obj.text = request.data['text']
	comment_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def comment_delete(request):
	
	comment_obj = Comment.objects.get(pk=request.data['id'])
	comment_obj.delete()
	
	return Response(None, status=status.HTTP_200_OK)
