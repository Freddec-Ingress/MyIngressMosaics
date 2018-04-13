#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def country_list(request):
	
	data = {
		
		'countries':[],
	}
	
	# Countries data
	
	country_results = Country.objects.all().order_by('name')
	for country_obj in country_results:
		
		country_data = {
			
			'id':country_obj.pk,
			'name':country_obj.name,
		}
		
		data['countries'].append(country_data)
	
	return Response(data, status=status.HTTP_200_OK)
