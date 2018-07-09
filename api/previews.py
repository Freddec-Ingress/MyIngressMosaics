#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *

from urllib.error import URLError
from urllib.request import Request



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def previews_cleaning_check(request):
	
	data = {
		'mosaics':[],
	}
	
	mosaic_results = Mosaic.objects.filter(small_preview_url__isnull=False, city__region__country__code='us')
	for mosaic_obj in mosaic_results:
		
		if mosaic_obj.small_preview_url == '':
			
			mosaic_obj.small_preview_url = None
			mosaic_obj.save()
			
		else:
			try:
				req = Request(mosaic_obj.small_preview_url, headers={'User-Agent': 'Mozilla/5.0'})
				urllib.request.urlopen(req)
		
			except URLError:
				data['mosaics'].append({'ref':mosaic_obj.ref, 'title':mosaic_obj.title, });
	
	return Response(data, status=status.HTTP_200_OK)
