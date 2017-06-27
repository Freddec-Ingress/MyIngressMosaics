#!/usr/bin/env python
# coding: utf-8

from rest_framework.response import Response

import hashlib



#---------------------------------------------------------------------------------------------------
def auto_logout(*args, **kwargs):
	
	return {'user': None}



#---------------------------------------------------------------------------------------------------
def save_data(strategy, details, user=None, *args, **kwargs):

	if user:
		pass



#---------------------------------------------------------------------------------------------------
def check_for_email(backend, uid, user=None, *args, **kwargs):
	
	if not kwargs['details'].get('email'):
		
		return Response({'error': 'Email wasn\'t provided by oauth provider'}, status=400)
