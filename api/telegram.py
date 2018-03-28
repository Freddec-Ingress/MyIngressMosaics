#!/usr/bin/env python
# coding: utf-8

import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((AllowAny, ))
def telegram_updates(request):
	
	if 'inline_query' in request.data:
		
		query_id = request.data['inline_query']['id']
		query_string = request.data['inline_query']['query']

		articles = []

		results = Mosaic.objects.filter(title__icontains=query_string)[:5]
		for mosaic_obj in results:
		
			preview_url = 'https://www.myingressmosaics.com/preview/' + mosaic_obj.ref
		
			article = InlineQueryResultArticle(
					id=mosaic_obj.ref,
					title=mosaic_obj.title,
					description=mosaic_obj.city.region.country.name + ', ' + mosaic_obj.city.region.name + ', ' + mosaic_obj.city.name + ', ' + str(mosaic_obj.missions.all().count()) + ' missions',
					thumb_url=preview_url, 
					input_message_content=InputTextMessageContent(
						message_text='' +
							'<b>' + mosaic_obj.title + '</b><br>' +
							mosaic_obj.city.region.country.name + ', ' + mosaic_obj.city.region.name + ', ' + mosaic_obj.city.name + '<br>' +
							str(mosaic_obj.missions.all().count()) + ' missions<br>' +
							'<a href="https://www.myingressmosaics.com/mosaic/' + mosaic_obj.ref + '">MIM Link</a><br>' +
							'<img src="' + preview_url + '">' +
						'',
						parse_mode='HTML'
					)
				)
				
			articles.append(article)
			
		bot = telepot.Bot('539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0')
		bot.answerInlineQuery(query_id, articles)
		
	return Response(None, status=status.HTTP_200_OK)
