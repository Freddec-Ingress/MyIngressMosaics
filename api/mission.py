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
def mission_reorder(request):
	
	mission_obj = Mission.objects.get(id=request.data['ref'])
	mission_obj.order = request.data['order']
	mission_obj.save()
	
	return Response(None, status=status.HTTP_200_OK)
