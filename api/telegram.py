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
	
	bot = telepot.Bot('539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0')
	
	response_url = 'https://api.telegram.org/bot539679576:AAFC6QR0d8aTKd5sckEWWEFfwsNq5W5Rar0/sendMessage'
	response_txt = ''

	# Inline query
	
	if 'inline_query' in request.data:
		
		query_id = request.data['inline_query']['id']
		query_string = request.data['inline_query']['query']

		articles = []

		results = Mosaic.objects.filter(title__icontains=query_string)
		for mosaic_obj in results:
		
			article = InlineQueryResultArticle(
					id=mosaic_obj.ref,
					title=mosaic_obj.title,
					description=mosaic_obj.city.region.country.name + ' > ' + mosaic_obj.city.region.name + ' > ' + mosaic_obj.city.name,
					thumb_width=0,
					input_message_content=InputTextMessageContent(
						message_text='<a href="https://www.myingressmosaics.com/fr/mosaic/' + mosaic_obj.ref + '">' + MIM Link + '</a>',
						parse_mode='HTML'
					)
				)
				
			articles.append(article)
			
		bot.answerInlineQuery(query_id, articles)
		
		return Response(None, status=status.HTTP_200_OK)
		
	# Unknown command
	
	else:
		response_txt = 'Unknown command... sorry.'
	
	# Send response
	
	params = {
		'chat_id': request.data['message']['chat']['id'],
		'text': response_txt,
		'parse_mode': 'HTML',
		'disable_web_page_preview': True,
	}
	
	requests.post(response_url, data=params)

	return Response(None, status=status.HTTP_200_OK)
