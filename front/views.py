#!/usr/bin/env python
# coding: utf-8

import io

from datetime import datetime, timedelta

from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import render
from django.utils.translation import gettext as _

from api.models import *

from urllib.request import Request

from PIL import Image



#---------------------------------------------------------------------------------------------------
def sitemap(request):

	text = ''
	text += '<?xml version="1.0" encoding="UTF-8"?>'
	text += '<urlset'
	text += '	xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
	text += '	xmlns:xhtml="http://www.w3.org/1999/xhtml"'
	
	# Static URLs
	
	text += '<url>'
	text += '	<loc>https://www.myingressmosaics.com</loc><changefreq>daily</changefreq>'
	text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/" />'
	text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/" />'
	text += '</url>'
	
	text += '<url>'
	text += '	<loc>https://www.myingressmosaics.com/map</loc><changefreq>daily</changefreq>'
	text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/map" />'
	text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/map" />'
	text += '</url>'
	
	text += '<url>'
	text += '	<loc>https://www.myingressmosaics.com/search</loc><changefreq>daily</changefreq>'
	text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/search" />'
	text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/search" />'
	text += '</url>'
	
	text += '<url>'
	text += '	<loc>https://www.myingressmosaics.com/profile</loc><changefreq>daily</changefreq>'
	text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/profile" />'
	text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/profile" />'
	text += '</url>'
	
	text += '<url>'
	text += '	<loc>https://www.myingressmosaics.com/registration</loc><changefreq>daily</changefreq>'
	text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/registration" />'
	text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/registration" />'
	text += '</url>'
	
	# Mosaic URLs
	
	mosaics = Mosaic.objects.all()
	for mosaic in mosaics:
		text += '<url>'
		text += '	<loc>https://www.myingressmosaics.com/mosaic/' + mosaic.ref + '</loc><changefreq>monthly</changefreq></url>'
		text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/mosaic/' + mosaic.ref + '" />'
		text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/mosaic/' + mosaic.ref + '" />'
		text += '</url>'

	# Country URLs
	
	countries = Country.objects.all()
	for country in countries:
		text += '<url>'
		text += '	<loc>https://www.myingressmosaics.com/world/' + country.name + '</loc><changefreq>daily</changefreq></url>'
		text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/world/' + country.name + '" />'
		text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/world/' + country.name + '" />'
		text += '</url>'

	# Region URLs
	
	regions = Region.objects.all()
	for region in regions:
		text += '<url>'
		text += '	<loc>https://www.myingressmosaics.com/world/' + region.country.name + '/' + region.name + '</loc><changefreq>daily</changefreq></url>'
		text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/world/' + region.country.name + '/' + region.name + '" />'
		text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/world/' + region.country.name + '/' + region.name + '" />'
		text += '</url>'

	# Creator URLs
	
	creators = Mission.objects.order_by('creator').values('creator').distinct()
	for creator in creators:
		if creator['creator']:
			text += '<url>'
			text += '	<loc>https://www.myingressmosaics.com/creator/' + creator['creator'] + '</loc><changefreq>daily</changefreq></url>'
			text += '	<xhtml:link rel="alternate" hreflang="en" href="https://www.myingressmosaics.com/en/creator/' + creator['creator'] + '" />'
			text += '	<xhtml:link rel="alternate" hreflang="fr" href="https://www.myingressmosaics.com/fr/creator/' + creator['creator'] + '" />'
			text += '</url>'
			
	text += '</urlset>'
	
	response = HttpResponse(text, content_type = 'text/plain')
	return response



#---------------------------------------------------------------------------------------------------
def preview(request, ref):

	mosaic_obj = Mosaic.objects.get(ref=ref)

	if not mosaic_obj.big_preview_url:
		
		imgByteArr = mosaic_obj.generatePreview(100)
		response = cloudinary.uploader.upload(imgByteArr, public_id=mosaic_obj.ref + '_100')
		mosaic_obj.big_preview_url = response['url']
		
		mosaic_obj.save()
		
	else:
		
		req = Request(mosaic_obj.big_preview_url, headers={'User-Agent': 'Mozilla/5.0'})
		file = io.BytesIO(urllib.request.urlopen(req).read())
		img = Image.open(file)
		
		imgByteArr = io.BytesIO()
		img.save(imgByteArr, format='PNG')
		imgByteArr = imgByteArr.getvalue()
	
	return HttpResponse(imgByteArr, content_type='image/png')



#---------------------------------------------------------------------------------------------------
def mosaic(request, ref):

	context = {
		
		'mosaic':None,

		'mission_count':0,
		'missions':[],
		
		'comment_count':0,
		'comments':[],
	}

	# Mosaic data
	
	mosaic_obj = Mosaic.objects.get(ref=ref)
	
	context['mosaic'] = {
		
		'id':mosaic_obj.pk,
		'ref':str(mosaic_obj.ref),
		'title':str(mosaic_obj.title),
		'owner_msg':str(mosaic_obj.owner_msg),

		'column_count':mosaic_obj.column_count,
		'portal_count':mosaic_obj.portal_count,
		'unique_count':mosaic_obj.unique_count,
		'mission_count':mosaic_obj.mission_count,
		'waypoint_count':mosaic_obj.waypoint_count,
		
		'distance': mosaic_obj.distance,
		
		'city_name':str(mosaic_obj.city.name),
		'region_name':str(mosaic_obj.city.region.name),
		'country_name':str(mosaic_obj.city.region.country.name),
		'country_code':str(mosaic_obj.city.region.country.code),
		
		'is_like':False,
		'is_todo':False,
		'is_complete':False,
		
		'likers': mosaic_obj.links.filter(type='like').count(),
		'todoers': mosaic_obj.links.filter(type='todo').count(),
		'completers': mosaic_obj.links.filter(type='complete').count(),
		
		'is_obsolete':mosaic_obj.obsolete,
		'has_unavailable_portals':False,
		
		'tags': [],
		'creators': [],
		
		'is_owned':False,
	}

	if not request.user.is_anonymous:
		
		if Link.objects.filter(mosaic=mosaic_obj, user=request.user, type='like').count() > 0:
			context['mosaic']['is_like'] = True

		if Link.objects.filter(mosaic=mosaic_obj, user=request.user, type='todo').count() > 0:
			context['mosaic']['is_todo'] = True

		if Link.objects.filter(mosaic=mosaic_obj, user=request.user, type='complete').count() > 0:
			context['mosaic']['is_complete'] = True
	
	# Missions data
	
	for mission_obj in mosaic_obj.missions.all().order_by('order'):

		mission_data = {
			
			'desc':mission_obj.desc,
			'title':mission_obj.title,
			'image':mission_obj.image,
			
			'has_unavailable_portals':False,
			
			'startLat':mission_obj.startLat,
			'startLng':mission_obj.startLng,
			
			'portals':[],
		}
		
		context['missions'].append(mission_data)
		
		# Creators data
		
		creator_data = {
			
			'name':str(mission_obj.creator),
			'faction':str(mission_obj.faction),
		}
		
		if creator_data not in context['mosaic']['creators']:
			context['mosaic']['creators'].append(creator_data)
			
		if not request.user.is_anonymous and request.user.profile.agent_name and mission_obj.creator == request.user.profile.agent_name:
			context['mosaic']['is_owned'] = True
			
		# Portals data
		
		temp_portal_data = []
		
		jsondata = json.loads(mission_obj.data)
		
		if len(jsondata) > 9:
			for portal in jsondata[9]:
			
				lat = 0.0
				lng = 0.0
				
				type = 'portal'

				if portal[5]:
					
					if portal[5][0] == 'f':
						lat = portal[5][1] / 1000000.0
						lng = portal[5][2] / 1000000.0
						
						type = 'viewpoint'

					if portal[5][0] == 'p':
						lat = portal[5][2] / 1000000.0
						lng = portal[5][3] / 1000000.0

				portal_data = {
					
					'ref':portal[1],
					'lat':lat,
					'lng':lng,
					'type':type,
					'title':portal[2],
					'action':portal[4],
				}
				
				if portal_data['title'] == 'Unavailable':
					context['mosaic']['has_unavailable_portals'] = True
					mission_data['has_unavailable_portals'] = True

				mission_data['portals'].append(portal_data)

	if request.user.is_superuser:
		context['mosaic']['is_owned'] = True
		
	# Comments data
	
	for comment_obj in mosaic_obj.comments.all().order_by('-create_date'):

		comment_data = {
			
			'text':comment_obj.text,

			'user_name':comment_obj.user.username,
			'user_faction':comment_obj.user.profile.faction,
		}
		
		context['comments'].append(comment_data)
	
	# Tags data
	
	if mosaic_obj.tags:
		
		tag_results = Tag.objects.all().order_by('-pk')
		for tag_obj in tag_results:
			
			if tag_obj.value in mosaic_obj.tags:
			
				tag_data = {
					
					'value':tag_obj.value,
					'label':tag_obj.label,
				}
				
				context['mosaic']['tags'].append(tag_data)
	
	context['comment_count'] = len(context['comments'])
	context['mission_count'] = len(context['missions'])
	
	return render(request, 'mosaic.html', context)



#---------------------------------------------------------------------------------------------------
def manage(request, ref):

	data = {
		
		'not_allowed':True,
		
		'mosaic':None,
		'missions':[],
	}
	
	# Mosaic data
	
	mosaic_obj = Mosaic.objects.get(ref=ref)
	
	data['mosaic'] = {
		
		'id':mosaic_obj.pk,
		'ref':mosaic_obj.ref,
		'title':mosaic_obj.title,
		'owner_msg':mosaic_obj.owner_msg,
		
		'city_name':mosaic_obj.city.name,
		'region_name':mosaic_obj.city.region.name,
		'country_name':mosaic_obj.city.region.country.name,
	}
	
	# Missions data
	
	for mission_obj in mosaic_obj.missions.all().order_by('order'):

		mission_data = {
			
			'id':mission_obj.pk,
			'ref':mission_obj.ref,
			'title':mission_obj.title,
			'order':mission_obj.order,
			'toremove':False,
		}
		
		data['missions'].append(mission_data)
		
	# Authorization
	
	if request.user.is_superuser or (request.user.profile.agent_name and request.user.profile.agent_name in mosaic_obj.creators):
		data['not_allowed'] = False
	
	return render(request, 'manage.html', data)
	
	
	
#---------------------------------------------------------------------------------------------------
def registration(request, search_string = ''):
	
	context = {
		
		'search_string':search_string.replace('\'', '\\\''),
		
		'potential_count':0,
		'countries': [],
		'tags':[],
	}

	countries = Country.objects.all().order_by('name')
	for country in countries:
		
		potentials_results = country.potentials.order_by('city__name', '-mission_count', 'title')
		if potentials_results.count() > 0:
			
			country_data = {
				
				'name':country.name,
				'open':False,
				
				'potentials':[],
			}
			
			for potential_obj in potentials_results:
				country_data['potentials'].append(potential_obj.getOverviewData())
			
			context['potential_count'] += len(country_data['potentials'])
			context['countries'].append(country_data)

	tag_results = Tag.objects.filter(active=True).order_by('-pk')
	for tag_obj in tag_results:

		tag_data = {
			
			'label':tag_obj.label,
			'value':tag_obj.value,
		}
		
		context['tags'].append(tag_data)
	
	return render(request, 'registration.html', context)
	
	
	
#---------------------------------------------------------------------------------------------------
def search(request, search_string = ''):
	
	context = {
		
		'search_string':search_string.replace('\'', '\\\''),
		
		'tags':[],
	}

	tag_results = Tag.objects.all().order_by('-pk')
	for tag_obj in tag_results:

		tag_data = {
			
			'label':tag_obj.label,
			'value':tag_obj.value,
			'count':Mosaic.objects.filter(tags__icontains=tag_obj.value+'|').count(),
		}
		
		context['tags'].append(tag_data)
	
	return render(request, 'search.html', context)
	
	
	
#---------------------------------------------------------------------------------------------------
def tag(request, tag):
	
	tag_obj = Tag.objects.get(value=tag)
	
	tag_data = {
		
		'label':tag_obj.label,
		'value':tag_obj.value,
		
		'desc':tag_obj.desc,
		
		'tg_url':tag_obj.tg_url,
		'gplus_url':tag_obj.gplus_url,
		
		'mosaics':[],
	}
	
	mosaic_results = Mosaic.objects.filter(tags__icontains=tag_obj.value+'|').order_by('city__name', 'title')
	for mosaic_obj in mosaic_results:
		tag_data['mosaics'].append(mosaic_obj.getOverviewData())
	
	return render(request, 'tag.html', tag_data)


	
#---------------------------------------------------------------------------------------------------
def profile(request):
	
	context = {
		
		'name':None,
		'faction':None,
		'picture':None,
		'agent_name':None,
		
		'like_count':0,
		'todo_count':0,
		'notif_count':0,
		'mosaic_count':0,
		'mission_count':0,
		'complete_count':0,
		
		'likes':[],
		'todos':[],
		'notifs':[],
		'mosaics':[],
		'missions':[],
		'completes':[],
	}
		
	if not request.user.is_anonymous():
		
		context['name'] = str(request.user.username),
		context['faction'] = str(request.user.profile.faction),
		context['picture'] = str(request.user.profile.picture),
		context['agent_name'] = str(request.user.profile.agent_name),

		# Mosaics data
		
		if request.user.profile.agent_name:
			results = Mosaic.objects.filter(creators__contains=request.user.profile.agent_name)
			for mosaic_obj in results:
				context['mosaics'].append(mosaic_obj.getOverviewData())

		# Missions data
			
		if request.user.profile.agent_name:
			results = Mission.objects.filter(mosaic__isnull=True, creator=request.user.profile.agent_name)
			for mission_obj in results:
				context['missions'].append(mission_obj.getOverviewData())

		# Likes data
				
		results = Link.objects.filter(user=request.user, type='like')
		for link_obj in results:
			context['likes'].append(link_obj.mosaic.getOverviewData())
		
		# Todos data
		
		results = Link.objects.filter(user=request.user, type='todo')
		for link_obj in results:
			context['todos'].append(link_obj.mosaic.getOverviewData())
		
		# Completes data
		
		results = Link.objects.filter(user=request.user, type='complete')
		for link_obj in results:
			context['completes'].append(link_obj.mosaic.getOverviewData())
		
		# Notifs data
		
		results = Notif.objects.filter(user=request.user)
		for notif_obj in results:
			
			notif_data = {
				
				'city_name':None,
				'region_name':None,
				'country_name':notif_obj.country.name,
			}
			
			if notif_obj.city: notif_data['city_name'] = notif_obj.city.name
			if notif_obj.region: notif_data['region_name'] = notif_obj.region.name
			
			context['notifs'].append(notif_data)
		
		context['like_count'] = len(context['likes'])
		context['todo_count'] = len(context['todos'])
		context['notif_count'] = len(context['notifs'])
		context['mosaic_count'] = len(context['mosaics'])
		context['mission_count'] = len(context['missions'])
		context['complete_count'] = len(context['completes'])
		
		context['likes'] = json.dumps(context['likes'])
		context['todos'] = json.dumps(context['todos'])
		context['notifs'] = json.dumps(context['notifs'])
		context['mosaics'] = json.dumps(context['mosaics'])
		context['missions'] = json.dumps(context['missions'])
		context['completes'] = json.dumps(context['completes'])

	return render(request, 'profile.html', context)

	
	
#---------------------------------------------------------------------------------------------------
def map(request, location_name = ''):
	
	context = {
		'location_name': location_name,
	}
	
	return render(request, 'map.html', context)



#---------------------------------------------------------------------------------------------------
def city(request, country_name, region_name, city_name):
	
	data = {
		
		'city':None,
		
		'mosaic_count':0,
		'mosaics':[],
		
		'potential_count':0,
		'potentials':[],
		
		'mosaics_date_indexes':[],
		'mosaics_name_indexes':[],
		'mosaics_uniques_indexes':[],
		'mosaics_missions_indexes':[],
	}
	
	# City data
	
	city_obj = City.objects.filter(name=city_name).filter(Q(region__name=region_name) | Q(region__locale=region_name)).filter(Q(region__country__name=country_name) | Q(region__country__locale=country_name))
	city_obj = city_obj[0]
	
	data['city'] = {
		
		'region_name':str(city_obj.region.name),
		'country_code':str(city_obj.region.country.code),
		'country_name':str(city_obj.region.country.name),
		
		'name':str(city_obj.name),
		
		'notified':False,
	}
	
	if not request.user.is_anonymous():
		results = Notif.objects.filter(user=request.user, country=city_obj.region.country, region=city_obj.region, city=city_obj)
		if results.count() > 0:
			data['city']['notified'] = True

	# Mosaics data
	
	results = city_obj.mosaics.all()
	for mosaic_obj in results:
		mosaic_data = mosaic_obj.getOverviewData()
		
		data['mosaics'].append(mosaic_data)
		data['mosaic_count'] += 1

		# Name indexes data
		
		name_index = str(mosaic_obj.title[0])
		if name_index not in data['mosaics_name_indexes']:
			data['mosaics_name_indexes'].append(name_index)

		# Uniques indexes data
		
		uniques_index = int(mosaic_obj.unique_count / 100)
		if uniques_index not in data['mosaics_uniques_indexes']:
			data['mosaics_uniques_indexes'].append(uniques_index)

		# Missions indexes data
		
		missions_index = mosaic_data['mission_count']
		if missions_index not in data['mosaics_missions_indexes']:
			data['mosaics_missions_indexes'].append(missions_index)
	
	# Potentials data
	
	potentials = city_obj.potentials.all()
	for potential_obj in potentials:
		data['potentials'].append(potential_obj.getOverviewData())
		data['potential_count'] += 1
	
	# Date indexes data
	
	for index in range(1, int(data['mosaic_count'] / 25) + 2):
		data['mosaics_date_indexes'].append(index)
	
	# Name indexes data
	
	data['mosaics_name_indexes'].sort()
			
	# Uniques indexes data
	
	data['mosaics_uniques_indexes'].sort()
			
	# Missions indexes data
	
	data['mosaics_missions_indexes'].sort()
	
	data['mosaics'] = json.dumps(data['mosaics'])
	data['potentials'] = json.dumps(data['potentials'])
	
	data['mosaics_date_indexes'] = json.dumps(data['mosaics_date_indexes'])
	data['mosaics_name_indexes'] = json.dumps(data['mosaics_name_indexes'])
	data['mosaics_uniques_indexes'] = json.dumps(data['mosaics_uniques_indexes'])
	data['mosaics_missions_indexes'] = json.dumps(data['mosaics_missions_indexes'])
	
	return render(request, 'city.html', data)



#---------------------------------------------------------------------------------------------------
def region(request, country_name, region_name):
	
	data = {
		
		'region':None,
		
		'cities':[],
		
		'mosaic_count':0,
		'mosaics':[],
		
		'potential_count':0,
		'potentials':[],
		
		'mosaics_date_indexes':[],
		'mosaics_name_indexes':[],
		'mosaics_uniques_indexes':[],
		'mosaics_location_indexes':[],
		'mosaics_missions_indexes':[],
	}
	
	# Region data
	
	region_obj = Region.objects.get(country__name=country_name, name=region_name)
	
	data['region'] = {
		
		'country_code':str(region_obj.country.code),
		'country_name':str(region_obj.country.name),
		
		'name':str(region_obj.name),
		
		'notified':False,
	}
	
	if not request.user.is_anonymous():
		notif_results = Notif.objects.filter(user=request.user, country=region_obj.country, region=region_obj, city__isnull=True)
		if notif_results.count() > 0:
			data['region']['notified'] = True

	# Cities data
	
	for city_obj in region_obj.cities.all():
	
		city_data = {
			
			'name':city_obj.name,
			'locale':city_obj.locale,
		}
		
		data['cities'].append(city_data)

		# Location indexes data
		
		location_index = str(city_obj.name[0])
		if location_index not in data['mosaics_location_indexes']:
			data['mosaics_location_indexes'].append(location_index)
		
		# Mosaics data
		
		mosaics = city_obj.mosaics.all()
		for mosaic_obj in mosaics:
			
			mosaic_data = mosaic_obj.getOverviewData()
			
			data['mosaics'].append(mosaic_data)
			data['mosaic_count'] += 1
			
			# Name indexes data
			
			name_index = str(mosaic_obj.title[0])
			if name_index not in data['mosaics_name_indexes']:
				data['mosaics_name_indexes'].append(name_index)
	
			# Uniques indexes data
			
			uniques_index = int(mosaic_obj.unique_count / 100)
			if uniques_index not in data['mosaics_uniques_indexes']:
				data['mosaics_uniques_indexes'].append(uniques_index)
	
			# Missions indexes data
			
			missions_index = mosaic_data['mission_count']
			if missions_index not in data['mosaics_missions_indexes']:
				data['mosaics_missions_indexes'].append(missions_index)
		
		# Potentials data
		
		potentials = city_obj.potentials.all()
		for potential_obj in potentials:
			
			data['potentials'].append(potential_obj.getOverviewData())
			
			data['potential_count'] += 1
			
	# Location indexes data
	
	data['mosaics_location_indexes'].sort()
	
	# Date indexes data
	
	for index in range(1, int(len(data['mosaics']) / 25) + 2):
		data['mosaics_date_indexes'].append(index)
			
	# Name indexes data
	
	data['mosaics_name_indexes'].sort()
			
	# Uniques indexes data
	
	data['mosaics_uniques_indexes'].sort()
			
	# Missions indexes data
	
	data['mosaics_missions_indexes'].sort()
	
	data['cities'] = json.dumps(data['cities'])
	data['mosaics'] = json.dumps(data['mosaics'])
	data['potentials'] = json.dumps(data['potentials'])
	
	data['mosaics_date_indexes'] = json.dumps(data['mosaics_date_indexes'])
	data['mosaics_name_indexes'] = json.dumps(data['mosaics_name_indexes'])
	data['mosaics_uniques_indexes'] = json.dumps(data['mosaics_uniques_indexes'])
	data['mosaics_location_indexes'] = json.dumps(data['mosaics_location_indexes'])
	data['mosaics_missions_indexes'] = json.dumps(data['mosaics_missions_indexes'])
		
	return render(request, 'region.html', data)
	
	
	
#---------------------------------------------------------------------------------------------------
def country(request, country_name):
	
	country_obj = Country.objects.get(name=country_name)
	
	context = {
		
		'country':{
			
			'name':str(country_obj.name),
			'code':str(country_obj.code),
			
			'notified':False,
		},
		
		'region_count':0,
		'regions':[],
	}
	
	if not request.user.is_anonymous():
		notif_results = Notif.objects.filter(user=request.user, country=country_obj, region__isnull=True, city__isnull=True)
		if notif_results.count() > 0:
			context['country']['notified'] = True
			
	for region in country_obj.regions.all():

		region_data = {
			
			'name':region.name,
			'locale':region.locale,
			
			'mosaic_count':Mosaic.objects.filter(city__region=region).count(),
			'potential_count':Potential.objects.filter(city__region=region).count(),
		}
		
		context['regions'].append(region_data)
		
	context['region_count'] = len(context['regions'])
	context['regions'] = json.dumps(context['regions'])
	
	return render(request, 'country.html', context)
	
	
	
#---------------------------------------------------------------------------------------------------
def world(request):
	
	context = {
		
		'mosaic_count':0,
		
		'country_count':[],
		'countries':[],
		
		'tags':[],
	}
	
	for country in Country.objects.all():

		country_data = {
			
			'name':country.name,
			'code':country.code,
			'label':_(country.name),
			'locale':country.locale,
			'mosaic_count':Mosaic.objects.filter(city__region__country=country).count(),
			'potential_count':Potential.objects.filter(city__region__country=country).count(),
		}
		
		context['countries'].append(country_data)
		context['mosaic_count'] += country_data['mosaic_count']
		
	tag_results = Tag.objects.all().order_by('-pk')
	for tag_obj in tag_results:

		tag_data = {
			
			'label':tag_obj.label,
			'value':tag_obj.value,
			'count':Mosaic.objects.filter(tags__icontains=tag_obj.value+'|').count(),
		}
		
		context['tags'].append(tag_data)
		
	context['country_count'] = len(context['countries'])
	context['countries'] = json.dumps(context['countries'])

	return render(request, 'world.html', context)



#---------------------------------------------------------------------------------------------------
def creator(request, creator_name):
	
	context = {
		
		'name':creator_name,
		'faction':None,
		
		'mosaics':[],
		'missions':[],
	}
	
	# Creator data
	
	results = Mission.objects.filter(creator=creator_name)
	if results.count() > 0:
		context['faction'] = results[0].faction

	# Mosaics data
	
	results = Mosaic.objects.filter(creators__contains=creator_name).order_by('city__name', 'title')
	for mosaic_obj in results:
		context['mosaics'].append(mosaic_obj.getOverviewData())

	# Missions data

	results = Mission.objects.filter(mosaic__isnull=True, creator=creator_name).order_by('title')
	for mission_obj in results:
		context['missions'].append(mission_obj.getOverviewData())
	
	return render(request, 'creator.html', context)



#---------------------------------------------------------------------------------------------------
def adm_im(request):
	
	data = {
		
		'countries':[],
	}
	
	imcountry_results = IMCountry.objects.all().order_by('-count')
	for imcountry_obj in imcountry_results:
		
		imcountry_data = {
			
			'id':imcountry_obj.pk,
			'name':imcountry_obj.name,
			
			'cities':[],
		}
		
		immosaic_results = IMMosaic.objects.filter(country_name=imcountry_obj.name, dead=False, excluded=False, registered=False)
		for immosaic_obj in immosaic_results:
			
			city_data = {
				
				'name':immosaic_obj.city_name,
				'region_name':immosaic_obj.region_name,
				'country_name':immosaic_obj.country_name,
			}
		
			imcountry_data['cities'].append(city_data)
			
		imcountry_data['cities'] = [dict(t) for t in set([tuple(d.items()) for d in imcountry_data['cities']])]
		if len(imcountry_data['cities']) > 0:
			data['countries'].append(imcountry_data)
		
	return render(request, 'adm_im.html', data)

	
	
#---------------------------------------------------------------------------------------------------
def adm_city(request):
	
	data = {
		
		'city_doublons':[],
	}
	
	city_results = City.objects.order_by('region__country__name', 'region__name', 'name').values('name', 'region__name', 'region__country__name').annotate(count=Count('pk')).filter(count__gt=1)
	for city_obj in city_results:
		
		city_data = {
			
			'name':city_obj['name'], 
			'region_name':city_obj['region__name'], 
			'country_name':city_obj['region__country__name'], 
		}
		
		data['city_doublons'].append(city_data)
	
	return render(request, 'adm_city.html', data)



#---------------------------------------------------------------------------------------------------
def adm_region(request):
	
	data = {
		
		'region_mosaics':[],
		'region_locales':[],
		'region_countries':[],
	}
	
	region_results = Region.objects.all().order_by('country__name', 'name')
	for region_obj in region_results:
		
		region_data = {
			
			'id':region_obj.id,
			'name':region_obj.name,
			
			'country_id':region_obj.country.id, 
			'country_name':region_obj.country.name, 
		}
		
		if region_obj.cities.all().count() < 1:
			data['region_mosaics'].append(region_data)
		
		if not region_obj.locale:
			data['region_locales'].append(region_data)
		
		if region_obj.name == region_obj.country.name:
			data['region_countries'].append(region_data)
			
	return render(request, 'adm_region.html', data)



#---------------------------------------------------------------------------------------------------
def adm_compare(request):
	
	data = {
		
		'cities':[],
		'countries':[],
	}
	
	imcountry_results = IMCountry.objects.all().order_by('-count')
	for imcountry_obj in imcountry_results:
		
		imcountry_data_date = imcountry_obj.update_date
		if imcountry_data_date: imcountry_data_date = imcountry_data_date.strftime('%m.%d.%Y')
		
		imcountry_data = {
			
			'id':imcountry_obj.pk,
			'name':imcountry_obj.name,
			'count':imcountry_obj.count,
			'update_date':imcountry_data_date,
			
			'compare_count':0,
			
			'diff':0,

			'regions':[],
		}
		
		imcountry_data['compare_count'] = IMMosaic.objects.filter(country_name=imcountry_obj.name).count()
		imcountry_data['diff'] = imcountry_data['compare_count'] - imcountry_data['count']

		imregion_results = imcountry_obj.regions.all().order_by('-count')
		for imregion_obj in imregion_results:
			
			imregion_data_date = imregion_obj.update_date
			if imregion_data_date: imregion_data_date = imregion_data_date.strftime('%m.%d.%Y')
			
			imregion_data = {
				
				'id':imregion_obj.pk,
				'name':imregion_obj.name,
				'count':imregion_obj.count,
				'update_date':imregion_data_date,
				
				'compare_count':0,
				
				'diff':0,

				'extras':[],
				'mosaics':[],
			}
			
			imregion_data['compare_count'] = IMMosaic.objects.filter(country_name=imcountry_obj.name, region_name=imregion_obj.name).count()
			imregion_data['diff'] = imregion_data['compare_count'] - imregion_data['count']

			immosaic_results = IMMosaic.objects.filter(country_name=imcountry_obj.name, region_name=imregion_obj.name, dead=False, excluded=False, registered=False).order_by('name')
			for immosaic_obj in immosaic_results:
				
				mosaic_results = Mosaic.objects.filter(city__region__country__name=imcountry_obj.name, city__region__name=imregion_obj.name, title__iexact=immosaic_obj.name)
				if mosaic_results.count() > 0:
					
					immosaic_obj.registered=True
					immosaic_obj.save()
					
				else:
					
					immosaic_data_date = immosaic_obj.update_date
					if immosaic_data_date: immosaic_data_date = immosaic_data_date.strftime('%m.%d.%Y')
					
					immosaic_data = {
						
						'id':immosaic_obj.pk,
						'name':immosaic_obj.name,
						'count':immosaic_obj.count,
						'update_date':immosaic_data_date,
						
						'registered':immosaic_obj.registered,
						'excluded':immosaic_obj.excluded,
						'dead':immosaic_obj.dead,
					}
					
					imregion_data['mosaics'].append(immosaic_data)

			if imregion_obj.update_date:
				
				date_compare = imregion_obj.update_date - timedelta(hours=1)
				immosaic_results = IMMosaic.objects.filter(country_name=imcountry_obj.name, region_name=imregion_obj.name, update_date__isnull=True).order_by('name')
				for immosaic_obj in immosaic_results:
					
					immosaic_data_date = immosaic_obj.update_date
					if immosaic_data_date: immosaic_data_date = immosaic_data_date.strftime('%m.%d.%Y')
					
					immosaic_data = {
						
						'id':immosaic_obj.pk,
						'name':immosaic_obj.name,
						'update_date':immosaic_data_date,
					}
					
					imregion_data['extras'].append(immosaic_data)

			imcountry_data['regions'].append(imregion_data)
		
		data['countries'].append(imcountry_data)
	
	return render(request, 'adm_compare.html', data)



#---------------------------------------------------------------------------------------------------
def adm_registration(request):

	context = {
		
		'potentials':[],
	}
	
	fieldname = 'name'
	results = Mission.objects.filter(mosaic__isnull=True, admin=True, validated=False).order_by(fieldname).values(fieldname, 'creator').annotate(count=Count(fieldname)).order_by('creator', '-count', 'name')
	for item in results:
		if item['count'] >= 3:
			
			obj = {
				'name':item[fieldname],
				'count':item['count'],
				
				'city':None,
				'region':None,
				'country':None,
			}
			
			context['potentials'].append(obj)
	
	return render(request, 'adm_registration.html', context)
