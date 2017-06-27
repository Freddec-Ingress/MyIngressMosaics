#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import *

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt



#---------------------------------------------------------------------------------------------------
@csrf_exempt
def ext_check(request):
	
	data = []
	
	import json
	obj = json.loads(request.body)
	
	for item in obj:
	
		result = Mission.objects.filter(ref = item['mid'])
		if result.count() > 0:
			data.append({'mid':item['mid'], 'status': 'registered'})
		else:
			data.append({'mid':item['mid'], 'status': 'notregistered'})
	
	from django.http import JsonResponse
	return JsonResponse({'data': data})



#---------------------------------------------------------------------------------------------------
class ExtensionViewSet(viewsets.ViewSet):
	
	permission_classes = AllowAny, 
    
	def register(self, request):

		import json
		obj = json.loads(request.body)
		
		mission = None
		
		results = Mission.objects.filter(ref=obj[0])
		if (results.count() < 1):
			
			mission = Mission(ref=obj[0], title=obj[1], desc=obj[2], creator=obj[3], faction=obj[4], image=obj[10], registerer=obj[11],
							  data=request.body)
			mission.save()
			
			order = 1
			
			for item in obj[9]:
				
				if item[5][0] == 'f':
				
					portal = Portal(mission=mission, lat=(item[5][1]/1000000.0), lng=(item[5][2]/1000000.0), order=order, title=item[2])
					portal.save()
					
				else:
				
					portal = Portal(mission=mission, lat=(item[5][2]/1000000.0), lng=(item[5][3]/1000000.0), order=order, title=item[2])
					portal.save()
				
				order += 1
		
			mission.computeInternalData()
		
		return Response(None, status=status.HTTP_200_OK)
