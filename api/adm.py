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
def adm_compare(request):
	
	data = { 'countries':[] }
	
	results = IMCountry.objects.all()
	for item in results:
		
		compare_count = 0
		compare = Country.objects.filter(name=item.name)
		if compare.count() > 0:
			compare = compare[0]
			compare_count = Mosaic.objects.filter(city__region__country=compare).count()
		
		country = {
			'name': item.name,
			'diff': item.count - compare_count,
		}
		
		data['countries'].append(country)
	
	return Response(data, status=status.HTTP_200_OK)
