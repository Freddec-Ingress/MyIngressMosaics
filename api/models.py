#!/usr/bin/env python
# coding: utf-8

from math import *

from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver

from django.contrib.auth.models import User

from django.utils.encoding import python_2_unicode_compatible



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Profile(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	team = models.CharField(max_length=32, null=True, blank=True)
	level = models.IntegerField(null=True, blank=True)
	
	def __str__(self):
		return 'Profil: ' + self.user.username
	   
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()



#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Creator(models.Model):

	name = models.CharField(max_length=32, default='')
	faction = models.CharField(max_length=8, default='')
	
	def __str__(self):
		return self.name



#---------------------------------------------------------------------------------------------------
from django.utils.crypto import get_random_string

def _createRef():
	return get_random_string(32)
	
@python_2_unicode_compatible
class Mosaic(models.Model):

	registerer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mosaics')
	
	creators = models.ManyToManyField('Creator')
	
	ref = models.CharField(max_length=32, default=_createRef, unique=True)
	cols = models.IntegerField(default=0)
	type = models.CharField(max_length=64, default='')
	desc = models.CharField(max_length=1024, default='')
	city = models.CharField(max_length=64, default='')
	count = models.IntegerField(default=0)
	title = models.CharField(max_length=128, default='')
	status = models.CharField(max_length=64, default='active')
	region = models.CharField(max_length=64, default='')
	country = models.CharField(max_length=64, default='')
	
	register_date = models.DateField(default=datetime.now)
	
	_distance = models.FloatField(default=0.0)
	
	_startLat = models.FloatField(default=0.0)
	_startLng = models.FloatField(default=0.0)
	
	def __str__(self):
		return self.title
	
	def minSerialize(self):
		
		data = {
			'ref': self.ref,
			'cols': self.cols,
			'type': self.type,
			'count': self.count,
			'title': self.title,
			
			'_distance': self._distance,
			
			'missions': [],
		}
			
		for item in self.missions.all().order_by('order'):
			
			mission_data = {
				'image': item.image,
			}
			
			data['missions'].append(mission_data)
			
		return data
		
	def serialize(self):
		
		data = {
			'registerer': {
				'name': self.registerer.username if self.registerer else '',
			},
			
			'creators': [],
			'missions': [],
			
			'ref': self.ref,
			'cols': self.cols,
			'type': self.type,
			'desc': self.desc,
			'city': self.city,
			'count': self.count,
			'title': self.title,
			'status': self.status,
			'region': self.region,
			'country': self.country,
			
			'register_date': self.register_date,
			
			'_distance': self._distance,
			
			'_startLat': self._startLat,
			'_startLng': self._startLng,
		}
		
		for item in self.creators.all():
			
			creator_data = {
				'name': item.name,
				'faction': item.faction,
			}
			
			data['creators'].append(creator_data)
		
		for item in self.missions.all().order_by('order'):
			
			item.checkPortal()
			
			mission_data = {
				'ref': item.ref,
				'title': item.title,
				'image': item.image,
				'order': item.order,
				'lat': item._startLat,
				'lng': item._startLng,
			}
			
			data['missions'].append(mission_data)
			
		return data
		
	
	
	def computeInternalData(self):
		
		missions = self.missions.order_by('order')
		if missions.count() > 0:
			
			self._startLat = missions[0]._startLat
			self._startLng = missions[0]._startLng
			
			dst = 0
			
			self.creators.clear()
			
			for i in range(0, missions.count() - 1):
				dst += missions[i]._distance
				
				result = Creator.objects.filter(name=missions[i].creator)
				if result.count() > 0:
					self.creators.add(result[0])
				else:
					creator = Creator(name=missions[i].creator, faction=missions[i].faction)
					creator.save()
					
					self.creators.add(creator)
	   
			self._distance = dst
			
			self.save()



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

	mosaic = models.ForeignKey('Mosaic', on_delete=models.SET_NULL, null=True, blank=True, related_name='missions')
	
	data = models.TextField()

	ref = models.CharField(max_length=64, default='')
	desc = models.TextField(default='')
	title = models.CharField(max_length=128, default='')
	image = models.CharField(max_length=256, default='')
	order = models.IntegerField(default=0)
	creator = models.CharField(max_length=32, default='')
	faction = models.CharField(max_length=8, default='')
	registerer = models.CharField(max_length=32, default='')

	_distance = models.FloatField(default=0.0)
	
	_startLat = models.FloatField(default=0.0)
	_startLng = models.FloatField(default=0.0)

	def __str__(self):
		return self.title

	def computeInternalData(self):
		
		portals = self.portals.order_by('order')
		if portals.count() > 0:
			
			for p in portals:
				
				if p.lat != 0.0 and p.lng != 0.0:
					
					self._startLat = p.lat
					self._startLng = p.lng
					
					break;
			
			dst = 0
			
			for i in range(0, portals.count() - 1):
				if portals[i].lat != 0.0 and portals[i].lng != 0.0 and portals[i+1].lat != 0.0 and portals[i+1].lng != 0.0:
					dst += getDistanceFromLatLng(portals[i].lat, portals[i].lng, portals[i+1].lat, portals[i+1].lng)
	   
			self._distance = dst
			
			self.save()

	def checkPortal(self):
		
		portals = self.portals.order_by('order')
		if portals.count() > 0:
			
			for p in portals:
				
				if p.lat != 0.0 and p.lng != 0.0:
					
					self._startLat = p.lat
					self._startLng = p.lng
					
					self.save()
					
					break
					


#---------------------------------------------------------------------------------------------------
@python_2_unicode_compatible
class Portal(models.Model):

	mission = models.ForeignKey('Mission', on_delete=models.CASCADE, null=True, blank=True, related_name='portals')

	lat = models.FloatField(default=0.0)
	lng = models.FloatField(default=0.0)
	order = models.IntegerField(default=-1)
	title = models.CharField(max_length=128, default='')

	def __str__(self):
		return self.mission.title + ' - ' + str(self.order) + ' - ' + self.title
