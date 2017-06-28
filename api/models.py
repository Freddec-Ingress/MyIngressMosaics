#!/usr/bin/env python
# coding: utf-8

from math import *

from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver

from django.contrib.auth.models import User



#---------------------------------------------------------------------------------------------------
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    team = models.CharField(max_length=32, null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return 'Profil: ' + self.user.username
       
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



#---------------------------------------------------------------------------------------------------
class Creator(models.Model):

    name = models.CharField(max_length=32, default='')
    faction = models.CharField(max_length=8, default='')
    
    def __unicode__(self):
        return self.name



#---------------------------------------------------------------------------------------------------
class Mosaic(models.Model):

    registered = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='mosaics')
    
    creators = models.ManyToManyField('Creator')
    
    ref = models.CharField(max_length=64, default='')
    rows = models.IntegerField(default=0)
    cols = models.IntegerField(default=0)
    type = models.CharField(max_length=64, default='')
    desc = models.CharField(max_length=1024, default='')
    city = models.CharField(max_length=64, default='')
    title = models.CharField(max_length=128, default='')
    status = models.CharField(max_length=64, default='')
    country = models.CharField(max_length=64, default='')
    
    register_date = models.DateField(default=datetime.now)
    
    _distance = models.FloatField(default=0.0)
    
    _startLat = models.FloatField(default=0.0)
    _startLng = models.FloatField(default=0.0)
    
    def __unicode__(self):
        return self.title



#---------------------------------------------------------------------------------------------------
def getDistanceFromLatLng(lat1, lng1, lat2, lng2):
    
    R = 6371.0; 
    
    dLat = radians(lat2 - lat1);
    dLng = radians(lng2 - lng1);
    
    a =  sin(dLat/2.0) * sin(dLat/2.0) + cos(radians(lat1)) * cos(radians(lat2)) *  sin(dLng/2.0) * sin(dLng/2.0)

    c = 2.0 * atan2(sqrt(a), sqrt(1.0-a)); 
    d = R * c;
    
    return d;



#---------------------------------------------------------------------------------------------------
class Mission(models.Model):

    mosaic = models.ForeignKey('Mosaic', on_delete=models.CASCADE, null=True, blank=True, related_name='missions')
    
    data = models.CharField(max_length=4096)

    ref = models.CharField(max_length=64, default='')
    desc = models.CharField(max_length=1024, default='')
    title = models.CharField(max_length=128, default='')
    image = models.CharField(max_length=256, default='')
    creator = models.CharField(max_length=32, default='')
    faction = models.CharField(max_length=8, default='')
    registerer = models.CharField(max_length=32, default='')

    _distance = models.FloatField(default=0.0)
    
    _startLat = models.FloatField(default=0.0)
    _startLng = models.FloatField(default=0.0)

    def __str__(self):
        return self.title
        
    def __unicode__(self):
        return self.title
        
    def computeInternalData(self):
        
        portals = self.portals.order_by('order')
        if portals.count() > 0:
            
            self._startLat = portals[0].lat
            self._startLng = portals[0].lng
            
            dst = 0
            
            for i in range(0, portals.count() - 1):
                dst += getDistanceFromLatLng(portals[i].lat, portals[i].lng, portals[i+1].lat, portals[i+1].lng)
       
            self._distance = dst
            
            self.save()



#---------------------------------------------------------------------------------------------------
class Portal(models.Model):

    mission = models.ForeignKey('Mission', on_delete=models.CASCADE, null=True, blank=True, related_name='portals')

    lat = models.FloatField(default=0.0)
    lng = models.FloatField(default=0.0)
    order = models.IntegerField(default=-1)
    title = models.CharField(max_length=128, default='')

    def __unicode__(self):
        return self.mission.title + ' - ' + str(self.order) + ' - ' + self.title
