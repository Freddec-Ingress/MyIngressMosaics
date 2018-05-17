#!/usr/bin/env python
# coding: utf-8

import io
import math
import json
import urllib

from urllib.request import Request

from math import *
from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver

from django.contrib.auth.models import User

from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible

from PIL import Image

import cloudinary



#---------------------------------------------------------------------------------------------------
cloudinary.config( 
	api_key='686619554325313', 
	api_secret='G8-FUHb3j3Zq5mIiK_1wQwGo8lg',
	cloud_name='freddec',
)



#---------------------------------------------------------------------------------------------------
def _createRef():
	return get_random_string(32)


	
#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Profile(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	locale = models.CharField(max_length=4, null=True, blank=True)
	faction = models.CharField(max_length=4, null=True, blank=True)
	picture = models.CharField(max_length=512, null=True, blank=True)
	
	agent_name = models.CharField(max_length=64, null=True, blank=True)
	family_name = models.CharField(max_length=64, null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		return 'Profil: ' + self.user.username + ' - ' + str(self.user.mosaics.count()) + ' - ' + str(self.user.links.count()) + ' - ' + str(self.user.notifications.count())
	   
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Country(models.Model):
	
	code = models.CharField(max_length=2, null=True, blank=True)
	name = models.CharField(max_length=512)
	locale = models.CharField(max_length=512, null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name
		


#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Region(models.Model):

	country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='regions')
	
	name = models.CharField(max_length=512)
	locale = models.CharField(max_length=512, null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class City(models.Model):

	region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='cities')
	
	name = models.CharField(max_length=512)
	locale = models.CharField(max_length=512, null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		text = self.name + ','
		if self.region: text += self.region.name + ','
		if self.region and self.region.country: text += self.region.country.name
		return text



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Mosaic(models.Model):

	city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='mosaics')
	
	ref = models.CharField(max_length=32, default=_createRef, unique=True)
	
	title = models.CharField(max_length=256)
	column_count = models.IntegerField(default=6)

	startLat = models.FloatField(null=True, blank=True)
	startLng = models.FloatField(null=True, blank=True)

	distance = models.FloatField(null=True, blank=True)

	creators = models.CharField(max_length=512, null=True, blank=True)

	registerer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mosaics')
	register_date = models.DateField(default=datetime.now)
	
	unique_count = models.IntegerField(null=True, blank=True)
	portal_count = models.IntegerField(null=True, blank=True)
	mission_count = models.IntegerField(null=True, blank=True)
	waypoint_count = models.IntegerField(null=True, blank=True)
	
	big_preview_url = models.CharField(max_length=256, null=True, blank=True)
	small_preview_url = models.CharField(max_length=256, null=True, blank=True)
	
	tags =  models.TextField(null=True, blank=True)
	
	obsolete = models.BooleanField(default=False)

	owner_msg =  models.TextField(null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.title + ' - ' + str(self.missions.count())
	
	
	
	# Internal data computing
	
	def computeInternalData(self):
	
		self.waypoint_count = 0
		self.mission_count = 0
		self.portal_count = 0
		self.unique_count = 0
		self.startLat = 0.0
		self.startLng = 0.0
		self.distance = 0.0
		self.creators = ''
		
		missions = []
		
		for item in self.missions.all().order_by('order'):
			
			self.mission_count += 1
			
			if self.startLat == 0.0 and self.startLng == 0.0 and item.startLat != 0.0 and item.startLng != 0.0:
				self.startLat = item.startLat
				self.startLng = item.startLng

			if item.creator not in self.creators:
				self.creators += '|' + item.creator + '|'
			
			self.distance += item.distance
		
			jsondata = json.loads(item.data)
			
			if len(jsondata) > 9:
				for portal in jsondata[9]:
			
					self.waypoint_count += 1
					
					if portal[5]:
						
						if portal[5][0] == 'p':
							type = 'portal'
							
						else:
							type = 'viewpoint'
					
						if type == 'portal':
							
							self.portal_count += 1
								
							to_add = True
							for mission_data in missions:
								for comp_portal_data in mission_data['portals']:
									if comp_portal_data['guid'] == portal[1]:
										to_add = False
										break
									
							if to_add:
								self.unique_count += 1
						
			missions.append({ 'portals':item.getPortalsData() })
			
		self.save()
	
	
	
	# Get overview data
	
	def getOverviewData(self):
		
		if not self.city:
			self.delete()
			return None
		
		mosaic_data = {
			
			'id':self.pk,
			
			'ref':self.ref,
			'title':self.title,
			
			'column_count':self.column_count,
			'unique_count':self.unique_count,
			'mission_count':self.mission_count,
			
			'city_name':self.city.name,
			'region_name':self.city.region.name,
			'country_code':self.city.region.country.code,
			'country_name':self.city.region.country.name,
			
			'is_obsolete':self.obsolete,
			'has_unavailable_portals':False,

			'tags':self.tags,

			'images':[],
		}
		
		for mission_obj in self.missions.all().order_by('-order'):
			mosaic_data['images'].append(str(mission_obj.image))

			portals_data = mission_obj.getPortalsData()
			for portal_data in portals_data:
				if portal_data['title'] == 'Unavailable':
					mosaic_data['has_unavailable_portals'] = True
					break
		
		return mosaic_data
	
	
	
	# Generate preview
	
	def generatePreview(self, dim):

		req = Request('https://www.myingressmosaics.com/static/img/mask.png', headers={'User-Agent': 'Mozilla/5.0'})
		maskfile = io.BytesIO(urllib.request.urlopen(req).read())
		maskimg = Image.open(maskfile)
		size = dim, dim
		maskimg.thumbnail(size, Image.ANTIALIAS)
		
		missions = self.missions.all().order_by('order')

		mission_count = missions.count()
		if mission_count < 1:
			return None
		
		img_width = dim * self.column_count
		
		row_count = int(math.ceil(mission_count / self.column_count))
		img_height = dim * row_count
				
		image = Image.new('RGBA', (img_width, img_height), (0, 0, 0))

		order = -1
		
		temp = 0;
		if mission_count > self.column_count:
			temp = (self.column_count - mission_count) % self.column_count;
			if temp < 0 or temp > (self.column_count - 1):
				temp = 0;
		
		for i in range(0, temp):
			order += 1
		
		for mission in reversed(missions):
	
			file = io.BytesIO(urllib.request.urlopen(mission.image + '=s' + str(int(dim * 0.9))).read())
			mimg = Image.open(file)
				
			order += 1 
			
			y = int(order / self.column_count)
			x = int(order - (y * self.column_count))
			
			xoffset = x * dim
			yoffset = y * dim
			
			padding = int(0.1 * dim / 2)
			
			image.paste(mimg, (int(xoffset+padding), int(yoffset+padding)));
			image.paste(maskimg, (int(xoffset), int(yoffset)), maskimg);
				
		imgByteArr = io.BytesIO()
		image.save(imgByteArr, format='PNG')
		imgByteArr = imgByteArr.getvalue()

		return imgByteArr



#---------------------------------------------------------------------------------------------------
def getDistanceFromLatLng(lat1, lng1, lat2, lng2):
	
	R = 6371.0; 
	
	dLat = radians(lat2 - lat1)
	dLng = radians(lng2 - lng1)
	
	a =  sin(dLat/2.0) * sin(dLat/2.0) + cos(radians(lat1)) * cos(radians(lat2)) *  sin(dLng/2.0) * sin(dLng/2.0)

	c = 2.0 * atan2(sqrt(a), sqrt(1.0-a)) 
	d = R * c
	
	return d



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Mission(models.Model):
	
	mosaic = models.ForeignKey('Mosaic', on_delete=models.SET_NULL, null=True, blank=True, related_name='missions')

	ref = models.CharField(max_length=64, null=True, blank=True, unique=True)

	data = models.TextField()

	name = models.CharField(max_length=256, null=True, blank=True)
	desc =  models.TextField(null=True, blank=True)
	order = models.IntegerField(null=True, blank=True)
	title = models.CharField(max_length=256, null=True, blank=True)
	image = models.CharField(max_length=256, null=True, blank=True)

	creator = models.CharField(max_length=32, null=True, blank=True)
	faction = models.CharField(max_length=32, null=True, blank=True)

	startLat = models.FloatField(null=True, blank=True)
	startLng = models.FloatField(null=True, blank=True)

	distance = models.FloatField(null=True, blank=True)

	admin = models.BooleanField(default=True)
	validated = models.BooleanField(default=False)

	registerer = models.TextField(null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		if self.title:
			return self.title
		else:
			return ''



	# Portals data
	
	def getPortalsData(self):
		
		data = []
		
		jsondata = json.loads(self.data)
		
		if len(jsondata) > 9:
			for portal in jsondata[9]:
			
				lat = 0.0
				lng = 0.0
				
				type = None
				
				if portal[5]:
					
					if portal[5][0] == 'f':
						lat = portal[5][1] / 1000000.0
						lng = portal[5][2] / 1000000.0
						
						type = 'viewpoint'
					
					if portal[5][0] == 'p':
						lat = portal[5][2] / 1000000.0
						lng = portal[5][3] / 1000000.0
						
						type = 'portal'
					
				pData = {
					'guid': portal[1],
					'lat': lat,
					'lng': lng,
					'type': type,
					'title': portal[2],
					'action': portal[4],
				}
	
				data.append(pData)
			
		return data



	# Internal data computing

	def computeInternalData(self):
	
		jsondata = json.loads(self.data)
		
		self.ref = jsondata[0]
		self.desc = jsondata[2]
		self.title = jsondata[1]
		self.image = jsondata[10]
		self.creator = jsondata[3]
		self.faction = jsondata[4]
		
		self.name = self.title
		self.name = self.name.replace('0', '')
		self.name = self.name.replace('1', '')
		self.name = self.name.replace('2', '')
		self.name = self.name.replace('3', '')
		self.name = self.name.replace('4', '')
		self.name = self.name.replace('5', '')
		self.name = self.name.replace('6', '')
		self.name = self.name.replace('7', '')
		self.name = self.name.replace('8', '')
		self.name = self.name.replace('9', '')
		self.name = self.name.replace('#', '')
		self.name = self.name.replace('０', '')
		self.name = self.name.replace('１', '')
		self.name = self.name.replace('２', '')
		self.name = self.name.replace('３', '')
		self.name = self.name.replace('４', '')
		self.name = self.name.replace('５', '')
		self.name = self.name.replace('６', '')
		self.name = self.name.replace('７', '')
		self.name = self.name.replace('８', '')
		self.name = self.name.replace('９', '')
		self.name = self.name.replace('①', '')
		self.name = self.name.replace('②', '')
		self.name = self.name.replace('③', '')
		self.name = self.name.replace('④', '')
		self.name = self.name.replace('⑤', '')
		self.name = self.name.replace('⑥', '')
		self.name = self.name.replace('.', '')
		self.name = self.name.replace('(', '')
		self.name = self.name.replace(')', '')
		self.name = self.name.replace('（', '')
		self.name = self.name.replace('）', '')
		self.name = self.name.replace('/', '')
		self.name = self.name.replace('[', '')
		self.name = self.name.replace(']', '')
		self.name = self.name.replace('【', '')
		self.name = self.name.replace('】', '')
		self.name = self.name.replace('-', '')
		self.name = self.name.replace('-', '')
		self.name = self.name.replace('－', '')
		self.name = self.name.replace('_', '')
		self.name = self.name.replace(':', '')
		self.name = self.name.replace('of ', '')
		self.name = self.name.replace(' of', '')
		self.name = self.name.replace('part ', '')
		self.name = self.name.replace(' part', '')
		self.name = self.name.replace('Part ', '')
		self.name = self.name.replace(' Part', '')
		self.name = self.name.replace('  ', ' ')
		self.name = self.name.replace('  ', ' ')
		self.name = self.name.replace('　', ' ')
		self.name = self.name.strip()
			
		portals = self.getPortalsData()

		self.startLat = 0.0
		self.startLng = 0.0
		self.distance = 0.0
		
		for i in range(0, len(portals) - 1):
		
			pData1 = portals[i]
			pData2 = portals[i+1]
			
			if pData1['lat'] != 0.0 and pData1['lng'] != 0.0 and self.startLat == 0.0 and self.startLng == 0.0:
				self.startLat = pData1['lat']
				self.startLng = pData1['lng']
				
			if pData1['lat'] != 0.0 and pData1['lng'] != 0.0 and pData2['lat'] != 0.0 and pData2['lng'] != 0.0:
				self.distance += getDistanceFromLatLng(pData1['lat'], pData1['lng'], pData2['lat'], pData2['lng'])
				
		if not self.registerer and jsondata[11]:
			self.registerer = jsondata[11]
				
		self.save()
	
	
	
	# Get overview data
	
	def getOverviewData(self):
		
		mission_data = {
			
			'id':self.pk,
			
			'ref':self.ref,
			'desc': self.desc,
			'title': self.title,
			'image': self.image,
			'creator': self.creator,
			'faction': self.faction,
			'startLat': self.startLat,
			'startLng': self.startLng,
		}
		
		return mission_data
	
	

#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Comment(models.Model):
	
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
	mosaic = models.ForeignKey('Mosaic', on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')

	text = models.TextField()
	
	create_date = models.DateField(default=datetime.now)
	update_date = models.DateField(default=datetime.now)
	
	# Admin displaying
	
	def __str__(self):
		text = ''
		if self.user:
			text += self.user.username
		text += ' - '
		if self.mosaic:
			text += self.mosaic.title
		return text
		


#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Search(models.Model):
	
	date = models.DateField(default=datetime.now)

	city = models.TextField(null=True, blank=True)
	region = models.TextField(null=True, blank=True)
	country = models.TextField(null=True, blank=True)

	name = models.TextField(null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		
		if self.city and self.region and self.country:
			return self.city + ', ' + self.region + ', ' + self.country
			
		if self.name:
			return self.name



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Link(models.Model):
	
	user = models.ForeignKey(User, related_name='links')
	mosaic = models.ForeignKey('Mosaic', related_name='links')

	type = models.CharField(max_length=32)
	
	# Admin displaying
	
	def __str__(self):

		return self.user.username + ' ' + self.type + ' ' + self.mosaic.title



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Potential(models.Model):
	
	city = models.ForeignKey(City, related_name='potentials')
	country = models.ForeignKey(Country, related_name='potentials', null=True, blank=True)
	
	title = models.CharField(max_length=256)
	mission_count = models.IntegerField()

	# Admin displaying
	
	def __str__(self):
		return self.title + ' - ' + str(self.mission_count)
	
	
	
	# Get overview data
	
	def getOverviewData(self):
		
		potential_data = {
			
			'title': self.title,
			'mission_count': self.mission_count,
			
			'city_name': self.city.name,
			'region_name': self.city.region.name,
			'country_name': self.country.name,
			'country_code': self.country.code,
		}
		
		return potential_data



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Notif(models.Model):
	
	user = models.ForeignKey(User, related_name='notifications')

	city = models.ForeignKey(City, null=True, blank=True, related_name='watchers')
	region = models.ForeignKey(Region, null=True, blank=True, related_name='watchers')
	country = models.ForeignKey(Country, null=True, blank=True, related_name='watchers')
	
	# Admin displayings
	
	def __str__(self):

		text = ''
		if self.city: text += self.city.__str__()
		if self.region: text += self.region.__str__()
		if self.country: text += self.country.__str__()

		return self.user.username + ' -> ' + text



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class IMCountry(models.Model):
	
	name = models.CharField(max_length=128)
	compare_name = models.CharField(max_length=128)
	
	count = models.IntegerField()
	
	update_date = models.DateField(blank=True, null=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class IMRegion(models.Model):

	country = models.ForeignKey(IMCountry, related_name='regions')
	
	name = models.CharField(max_length=128)
	compare_name = models.CharField(max_length=128)
	
	count = models.IntegerField()
	
	update_date = models.DateField(blank=True, null=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class IMCity(models.Model):

	region = models.ForeignKey(IMRegion, related_name='cities')
	
	name = models.CharField(max_length=128)
	compare_name = models.CharField(max_length=128)
	
	count = models.IntegerField()
	
	done = models.BooleanField(default=False)
	
	update_date = models.DateField(blank=True, null=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class IMMosaic(models.Model):

	country_name = models.CharField(max_length=128)
	region_name = models.CharField(max_length=128)
	city_name = models.CharField(max_length=128)
	
	name = models.CharField(max_length=128)
	count = models.IntegerField()
	
	dead = models.BooleanField(default=False)
	excluded = models.BooleanField(default=False)
	registered = models.BooleanField(default=False)
	processed = models.BooleanField(default=False)
	
	update_date = models.DateField(blank=True, null=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Waiting(models.Model):
	
	ref = models.CharField(max_length=32, default=_createRef, unique=True)
	
	city = models.ForeignKey(City, related_name='waitings')
	region = models.ForeignKey(Region, related_name='waitings')
	country = models.ForeignKey(Country, related_name='waitings')
	
	title = models.CharField(max_length=256)
	
	mission_refs = models.TextField()
	mission_count = models.IntegerField()
	mission_missing = models.TextField()
	
	# Admin displaying
	
	def __str__(self):
		return self.title + ' - ' + str(self.mission_count)



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Tag(models.Model):

	label = models.CharField(max_length=256)
	value = models.CharField(max_length=256)
	
	desc = models.TextField(blank=True, null=True)
	
	tg_url = models.CharField(max_length=256, blank=True, null=True)
	gplus_url = models.CharField(max_length=256, blank=True, null=True)
	website_url = models.CharField(max_length=256, blank=True, null=True)

	image = models.CharField(max_length=256, blank=True, null=True)
	
	active = models.BooleanField(default=True)

	# Admin displaying
	
	def __str__(self):
		return self.label
