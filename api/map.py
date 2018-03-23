#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def map_getMosaics(request):
	
	data = []
	
	results = Mosaic.objects.filter(startLat__gte=request.data['sLat'], startLng__gte=request.data['sLng']).filter(startLat__lte=request.data['nLat'], startLng__lte=request.data['nLng'])
	for mosaic_obj in results:
		mosaic_data = mosaic_obj.getOverviewData()
		mosaic_data['startLat'] = mosaic_obj.startLat
		mosaic_data['startLng'] = mosaic_obj.startLng
		data.append(mosaic_data)

	return Response(data, status=status.HTTP_200_OK)
