#!/usr/bin/env python
# coding: utf-8

import re
import json

from math import *

from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver

from django.contrib.auth.models import User

from django.utils.encoding import python_2_unicode_compatible

import math, os
import urllib, io

from operator import itemgetter, attrgetter, methodcaller

from PIL import Image, ImageDraw, ImageFont



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Profile(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	faction = models.CharField(max_length=4, null=True, blank=True)
	family_name = models.CharField(max_length=64, null=True, blank=True)
	picture = models.CharField(max_length=512, null=True, blank=True)
	locale = models.CharField(max_length=4, null=True, blank=True)
	
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
		
	# Serialization
	
	def serialize(self):
		
		data = {
			
			'id': self.pk,
			'code': self.code,
			'name': self.name,
			'locale': self.locale,
		}
		
		return data



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Region(models.Model):

	country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='regions')
	
	name = models.CharField(max_length=512)
	locale = models.CharField(max_length=512, null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name
		
	# Serialization
	
	def serialize(self):
		
		data = {

			'country': self.country.serialize(),
			
			'id': self.pk,
			'name': self.name,
			'locale': self.locale,
			'city_count': self.cities.all().count(),
		}
		
		return data



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class City(models.Model):

	region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='cities')
	
	name = models.CharField(max_length=512)
	locale = models.CharField(max_length=512, null=True, blank=True)
	
	# Admin displaying
	
	def __str__(self):
		return self.name
		
	# Serialization
	
	def serialize(self):
		
		data = {

			'region': self.region.serialize(),

			'id': self.pk,
			'name': self.name,
			'locale': self.locale,
			'mosaic_count': self.mosaics.all().count(),
		}
		
		return data



#---------------------------------------------------------------------------------------------------
from django.utils.crypto import get_random_string

def _createRef():
	return get_random_string(32)
	
@python_2_unicode_compatible
class Mosaic(models.Model):

	ref = models.CharField(max_length=32, default=_createRef, unique=True)
	cols = models.IntegerField(default=6)
	type = models.CharField(max_length=64, default='sequence')
	tags =  models.TextField(null=True, blank=True)
	title = models.CharField(max_length=256)
	status = models.CharField(max_length=64, default='active')
	preview = models.CharField(max_length=1024, null=True, blank=True)
	portals = models.IntegerField(null=True, blank=True)
	uniques = models.IntegerField(null=True, blank=True)
	startLat = models.FloatField(null=True, blank=True)
	startLng = models.FloatField(null=True, blank=True)
	distance = models.FloatField(null=True, blank=True)
	creators = models.CharField(max_length=512, null=True, blank=True)
	registerer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mosaics')
	register_date = models.DateField(default=datetime.now)
	
	city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='mosaics')
	
	lovers = models.ManyToManyField(User, blank=True, related_name='mosaics_loved')
	completers = models.ManyToManyField(User, blank=True, related_name='mosaics_completed')
	
	# Admin displaying
	
	def __str__(self):
		return self.title + ' - ' + str(self.missions.count())
		
	# Generate preview
	
	def generatePreview(self):
		
		mosaic = self
		
		mcount = mosaic.missions.count()
		
		mosaic_rows = int(math.ceil(mcount / mosaic.cols))
		
		img_height = 32 + 20 + (100 * mosaic_rows)
		if (img_height < 352):
			img_height = 352
		
		image = Image.new('RGBA', (632, img_height), (0, 77, 64))
	
		draw = ImageDraw.Draw(image)
		draw.rectangle(((8, 8), (624, img_height - 52 + 24)), fill = 'black')
		
		fontfile = io.BytesIO(urllib.request.urlopen('https://www.myingressmosaics.com/static/fonts/coda-regular.ttf').read())
		
		font = ImageFont.truetype(fontfile, 15)
		draw.text((16, img_height - 25), 'MIM - MyIngressMosaics.com', fill=(255, 255, 255), font=font)
		
		realx = 0
		if mcount < mosaic.cols:
			realx = mcount * 100
		else:
			realx = mosaic.cols * 100
		
		realy = mosaic_rows * 100
		
		paddingX = 16 + (600 - realx) / 2
		
		if mosaic_rows < 4:
			paddingY = 16 + (300 - realy) / 2
		else:
			paddingY = 16
	
		maskfile = io.BytesIO(urllib.request.urlopen('https://www.myingressmosaics.com/static/img/mask.png').read())
		maskimg = Image.open(maskfile)
			
		for m in mosaic.missions.all():
	
			if 'Unavailable' not in m.ref:
				file = io.BytesIO(urllib.request.urlopen(m.image + '=s100').read())
				mimg = Image.open(file)
				
			order = mcount - m.order
			
			y = int(order / mosaic.cols)
			x = int(order - (y * mosaic.cols))
			
			xoffset = paddingX + (x * 100)
			yoffset = paddingY + (y * 100)
			
			if 'Unavailable' not in m.ref:
				image.paste(mimg, (int(xoffset), int(yoffset)));
				
			image.paste(maskimg, (int(xoffset), int(yoffset)), maskimg);
	
		imgByteArr = io.BytesIO()
		image.save(imgByteArr, format='PNG')
		imgByteArr = imgByteArr.getvalue()
	
		from django.core.files.storage import default_storage
#		name = '' + self.ref + '.png'
#		file = default_storage.save(name, imgByteArr)
		
		return default_storage.location
	
	# Internal data computing

	def computeInternalData(self):
	
		self.portals = 0
		self.uniques = 0
		self.startLat = 0.0
		self.startLng = 0.0
		self.distance = 0.0
		self.creators = ''
		
		portals = []
		missions = []
		
		for item in self.missions.all().order_by('order'):
			
			if 'Unavailable' not in item.ref:
				mData = item.detailsSerialize()
				
				missions.append(mData)
	
				self.portals += len(mData['portals'])
				
				portals += mData['portals']
				
				if mData['creator'] not in self.creators:
					self.creators += '|' + mData['creator'] + '|'

		self.uniques = len([dict(t) for t in set([tuple(d.items()) for d in portals])])
		
		for i in range(0, len(missions) - 1):
			
			mData1 = missions[i]
			mData2 = missions[i+1]
			
			if mData1['startLat'] != 0.0 and mData1['startLng'] != 0.0 and self.startLat == 0.0 and self.startLng == 0.0:
				self.startLat = mData1['startLat']
				self.startLng = mData1['startLng']
				
			self.distance += mData1['distance']
			
			if i < len(missions) - 2:
				
				pData1 = mData1['portals'][len(mData1['portals']) - 1]
				pData2 = mData2['portals'][0]
				
				if pData1['lat'] != 0.0 and pData1['lng'] != 0.0 and pData2['lat'] != 0.0 and pData2['lng'] != 0.0:
					self.distance += getDistanceFromLatLng(pData1['lat'], pData1['lng'], pData2['lat'], pData2['lng'])
					
		self.save()

	# Mini serialization
	
	def miniSerialize(self):
		
		data = {
			
			'id': self.pk,
			'ref': self.ref,
			'cols': self.cols,
			'name': self.title,
			'type': self.type,
			'city': { 'name': self.city.name },
			
			'missions': [],
		}
			
		for mission in self.missions.all().order_by('order'):
			
			mission_data = { 'image':mission.image }
			data['missions'].append(mission_data)
			
		return data

	# Map serialization
	
	def mapSerialize(self):
		
		data = {
			
			'ref': self.ref,
			'startLat': self.startLat,
			'startLng': self.startLng,
		}
			
		return data
	
	# Overview serialization
	
	def overviewSerialize(self):
		
		data = {
			
			'id': self.pk,
			'ref': self.ref,
			'cols': self.cols,
			'type': self.type,
			'title': self.title,
			'distance': self.distance,
			'has_fake': False,
			'startLat': self.startLat,
			'startLng': self.startLng,
			'uniques': self.uniques,
			
			'city': None,

			'missions': [],
		}
		
		if self.city:
			data['city'] = self.city.serialize()
		
		for item in self.missions.all().order_by('order'):
			
			if 'Unavailable' in item.ref:
				data['has_fake'] = True
			
			mission_data = item.imgSerialize()
			data['missions'].append(mission_data)
			
		return data
	
	# Details serialization
		
	def detailsSerialize(self):

		data = {
			
			'ref': self.ref,
			'cols': self.cols,
			'type': self.type,
			'city': self.city.serialize(),
			'title': self.title,
			'likers': self.links.filter(type='like').count(),
			'portals': self.portals,
			'uniques': self.uniques,
			'distance': self.distance,
			'startLat': self.startLat,
			'startLng': self.startLng,
			'completers': self.links.filter(type='complete').count(),
			'todoers': self.links.filter(type='todo').count(),
			
			'has_fake': False,
			'is_loved': False,
			'is_completed': False,
			
			'creators': [],
			'missions': [],
			'comments': [],
		}

		creators = []

		for item in self.missions.all().order_by('order'):
			
			if 'Unavailable' in item.ref:
				data['has_fake'] = True
			
			mData = item.detailsSerialize()
			data['missions'].append(mData)
			
			cData = {
				'name': mData['creator'],
				'faction': mData['faction'],
			}
			
			creators.append(cData)

		data['creators'] = [dict(t) for t in set([tuple(d.items()) for d in creators])]
		
		for item in Comment.objects.filter(mosaic=self).order_by('-update_date'):
			data['comments'].append(item.serialize())
		
		return data



#---------------------------------------------------------------------------------------------------
def getDistanceFromLatLng(lat1, lng1, lat2, lng2):
	
	R = 6371.0; 
	
	dLat = radians(lat2 - lat1)
	dLng = radians(lng2 - lng1)
	
	a =  sin(dLat/2.0) * sin(dLat/2.0) + cos(radians(lat1)) * cos(radians(lat2)) *  sin(dLng/2.0) * sin(dLng/2.0)

	c = 2.0 * atan2(sqrt(a), sqrt(1.0-a)) 
	d = R * c
	
	return d

@python_2_unicode_compatible
class Mission(models.Model):

	data = models.TextField()

	ref = models.CharField(max_length=64, null=True, blank=True, unique=True)
	desc =  models.TextField(null=True, blank=True)
	order = models.IntegerField(null=True, blank=True)
	name = models.CharField(max_length=256, null=True, blank=True)
	title = models.CharField(max_length=256, null=True, blank=True)
	image = models.CharField(max_length=256, null=True, blank=True)
	creator = models.CharField(max_length=32, null=True, blank=True)
	faction = models.CharField(max_length=32, null=True, blank=True)
	startLat = models.FloatField(null=True, blank=True)
	startLng = models.FloatField(null=True, blank=True)
	distance = models.FloatField(null=True, blank=True)
	registerer = models.TextField(null=True, blank=True)
	
	admin = models.BooleanField(default=True)
	validated = models.BooleanField(default=False)
	
	mosaic = models.ForeignKey('Mosaic', on_delete=models.SET_NULL, null=True, blank=True, related_name='missions')
	
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
		
	# Image serialization

	def imgSerialize(self):
		
		data = {
			
			'image': self.image,
		}
		
		return data

	# Map serialization

	def mapSerialize(self):
		
		data = {
			
			'ref': self.ref,
			'startLat': self.startLat,
			'startLng': self.startLng,
		}
		
		return data

	# Overview serialization

	def overviewSerialize(self):
		
		data = {
			
			'ref': self.ref,
			'desc': self.desc,
			'order': self.order,
			'title': self.title,
			'name': self.name,
			'image': self.image,
			'creator': self.creator,
			'faction': self.faction,
			'startLat': self.startLat,
			'startLng': self.startLng,
		}
		
		return data

	# Details serialization

	def detailsSerialize(self):
		
		data = {
			
			'ref': self.ref,
			'desc': self.desc,
			'image': self.image,
			'order': self.order,
			'title': self.title,
			'name': self.name,
			'creator': self.creator,
			'faction': self.faction,
			'startLat': self.startLat,
			'startLng': self.startLng,
			'distance': self.distance,
			
			'portals': [],
		}
		
		if 'Unavailable' not in self.ref:
			data['portals'] = self.getPortalsData()
		
		return data



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
		
	# Serialization
	
	def serialize(self):
		
		username = 'unknown'
		if self.user:
			text = self.user.username
		
		faction = 'unknown'
		if self.user:
			text = self.user.profile.faction
			
		data = {
			
			'id': self.pk,
			'username': username,
			'faction': faction,
			'text': self.text,
		}
			
		return data



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



@python_2_unicode_compatible
class Link(models.Model):
	
	user = models.ForeignKey(User, related_name='links')
	mosaic = models.ForeignKey('Mosaic', related_name='links')

	type = models.CharField(max_length=32)
	
	# Admin displaying
	
	def __str__(self):

		return self.user.username + ' ' + self.type + ' ' + self.mosaic.title



@python_2_unicode_compatible
class Potential(models.Model):
	
	title = models.CharField(max_length=256)

	count = models.IntegerField()
	
	city = models.ForeignKey(City, related_name='potentials')
	country = models.ForeignKey(Country, related_name='potentials', null=True, blank=True)
	
	creator = models.CharField(max_length=32, null=True, blank=True)
	faction = models.CharField(max_length=32, null=True, blank=True)
	
	# Admin displaying
	def __str__(self):
		return self.title + ' - ' + str(self.count)

	def overviewSerialize(self):
		
		data = {
			
			'id': self.pk,
			'title': self.title,
			'count': self.count,
			'city': self.city.serialize(),
		}
		
		return data



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



@python_2_unicode_compatible
class IMCountry(models.Model):
	
	name = models.CharField(max_length=128)
	compare_name = models.CharField(max_length=128)
	
	count = models.IntegerField()
	
	# Admin displaying
	def __str__(self):
		return self.name



@python_2_unicode_compatible
class IMRegion(models.Model):

	country = models.ForeignKey(IMCountry, related_name='regions')
	
	name = models.CharField(max_length=128)
	compare_name = models.CharField(max_length=128)
	
	count = models.IntegerField()
	
	# Admin displaying
	def __str__(self):
		return self.name



@python_2_unicode_compatible
class IMCity(models.Model):

	region = models.ForeignKey(IMRegion, related_name='cities')
	
	name = models.CharField(max_length=128)
	compare_name = models.CharField(max_length=128)
	
	count = models.IntegerField()
	
	# Admin displaying
	def __str__(self):
		return self.name



@python_2_unicode_compatible
class IMMosaic(models.Model):

	country_name = models.CharField(max_length=128)
	region_name = models.CharField(max_length=128)
	city_name = models.CharField(max_length=128)

	compare_name = models.CharField(max_length=128)
	
	name = models.CharField(max_length=128)
	count = models.IntegerField()
	
	dead = models.BooleanField(default=False)
	excluded = models.BooleanField(default=False)
	
	# Admin displaying
	def __str__(self):
		return self.name
