#!/usr/bin/env python
# coding: utf-8

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

	# Admin displaying
	
	def __str__(self):
		return 'Profil: ' + self.user.username + ' - ' + str(self.user.mosaics.count())
	   
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()



#---------------------------------------------------------------------------------------------------
from django.utils.crypto import get_random_string

def _createRef():
	return get_random_string(32)
	
@python_2_unicode_compatible
class Mosaic(models.Model):

	ref = models.CharField(max_length=32, default=_createRef, unique=True)
	cols = models.IntegerField(default=6)
	type = models.CharField(max_length=64, default='sequence')
	city = models.CharField(max_length=64, null=True, blank=True)
	title = models.CharField(max_length=256, default='')
	status = models.CharField(max_length=64, default='active')
	region = models.CharField(max_length=64, null=True, blank=True)
	country = models.CharField(max_length=64)
	preview = models.CharField(max_length=1024, null=True, blank=True)
	portals = models.IntegerField(null=True, blank=True)
	uniques = models.IntegerField(null=True, blank=True)
	startLat = models.FloatField(null=True, blank=True)
	startLng = models.FloatField(null=True, blank=True)
	distance = models.FloatField(null=True, blank=True)
	creators = models.CharField(max_length=512, null=True, blank=True)
	registerer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mosaics')
	register_date = models.DateField(default=datetime.now)
	
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
	
			file = io.BytesIO(urllib.request.urlopen(m.image + '=s100').read())
			mimg = Image.open(file)
			
			order = mcount - m.order
			
			y = int(order / mosaic.cols)
			x = int(order - (y * mosaic.cols))
			
			xoffset = paddingX + (x * 100)
			yoffset = paddingY + (y * 100)
			
			image.paste(mimg, (int(xoffset), int(yoffset)));
			image.paste(maskimg, (int(xoffset), int(yoffset)), maskimg);
	
		imgByteArr = io.BytesIO()
		image.save(imgByteArr, format='PNG')
		imgByteArr = imgByteArr.getvalue()
	
		from django.core.files.storage import default_storage
		name = '' + self.ref + '.png'
		file = default_storage.open(name, 'w')
		file.write(imgByteArr)
		file.close()
	
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
		self.generatePreview()
	
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
		
		location = self.city
		if not location: location = self.region
		if not location: location = self.country
		
		data = {
			
			'ref': self.ref,
			'cols': self.cols,
			'type': self.type,
			'title': self.title,
			'country': self.country,
			'distance': self.distance,
			
			'location': location,

			'missions': [],
		}
		
		for item in self.missions.all().order_by('order'):
			
			mission_data = item.imgSerialize()
			data['missions'].append(mission_data)
			
		return data
	
	# Details serialization
		
	def detailsSerialize(self):

		data = {
			
			'ref': self.ref,
			'cols': self.cols,
			'type': self.type,
			'city': self.city,
			'title': self.title,
			'region': self.region,
			'country': self.country,
			'portals': self.portals,
			'uniques': self.uniques,
			'distance': self.distance,
			'startLat': self.startLat,
			'startLng': self.startLng,
			
			'creators': [],
			'missions': [],
		}
		
		creators = []

		for item in self.missions.all().order_by('order'):
			
			mData = item.detailsSerialize()
			data['missions'].append(mData)
			
			cData = {
				'name': mData['creator'],
				'faction': mData['faction'],
			}
			
			creators.append(cData)

		data['creators'] = [dict(t) for t in set([tuple(d.items()) for d in creators])]

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
	title = models.CharField(max_length=256, null=True, blank=True)
	image = models.CharField(max_length=256, null=True, blank=True)
	creator = models.CharField(max_length=32, null=True, blank=True)
	faction = models.CharField(max_length=32, null=True, blank=True)
	startLat = models.FloatField(null=True, blank=True)
	startLng = models.FloatField(null=True, blank=True)
	distance = models.FloatField(null=True, blank=True)
			
	mosaic = models.ForeignKey('Mosaic', on_delete=models.SET_NULL, null=True, blank=True, related_name='missions')
	
	# Admin displaying
	
	def __str__(self):
		return self.title

	# Portals data
	
	def getPortalsData(self):
		
		data = []
		
		jsondata = json.loads(self.data)
		
		for portal in jsondata[9]:
			
			lat = 0.0
			lng = 0.0
			
			if portal[5]:
				
				if portal[5][0] == 'f':
					lat = portal[5][1] / 1000000.0
					lng = portal[5][2] / 1000000.0
				
				if portal[5][0] == 'p':
					lat = portal[5][2] / 1000000.0
					lng = portal[5][3] / 1000000.0
				
			pData = {
				'lat': lat,
				'lng': lng,
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
			'order': self.order,
			'title': self.title,
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
			'creator': self.creator,
			'faction': self.faction,
			'startLat': self.startLat,
			'startLng': self.startLng,
			'distance': self.distance,
			
			'portals': [],
		}
		
		data['portals'] = self.getPortalsData()
		
		return data
