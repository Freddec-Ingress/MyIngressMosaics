#!/usr/bin/env python
# coding: utf-8

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *



#---------------------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def adm_compare(request):
	
	data = { 'countries':[] }
	
	imc_results = IMCountry.objects.all()
	for imc_item in imc_results:
		
		c_compare_count = 0
		if not imc_item.compare_name:
			c_compare = Country.objects.filter(name=imc_item.name)
			if c_compare.count() > 0:
				c_compare = c_compare[0]
				imc_item.compare_name = c_compare.name
				imc_item.save()
				c_compare_count = Mosaic.objects.filter(city__region__country=c_compare).count()
				c_compare_count += Potential.objects.filter(city__region__country=c_compare).count()
		else:
			c_compare = Country.objects.filter(name=imc_item.compare_name)
			if c_compare.count() > 0:
				c_compare = c_compare[0]
				c_compare_count = Mosaic.objects.filter(city__region__country=c_compare).count()
				c_compare_count += Potential.objects.filter(city__region__country=c_compare).count()
		
		country = {
			'id':imc_item.pk,
			'name':imc_item.name,
			'count':imc_item.count,
			'compare_name':imc_item.compare_name,
			'compare_count':c_compare_count,
			'regions':[]
		}
		
		if c_compare_count > 0:
			imr_results = imc_item.regions.all()
			for imr_item in imr_results:
			
				r_compare_count = 0
				if not imr_item.compare_name:
					r_compare = Region.objects.filter(country=c_compare, name=imr_item.name)
					if r_compare.count() > 0:
						r_compare = r_compare[0]
						imr_item.compare_name = r_compare.name
						imr_item.save()
						r_compare_count = Mosaic.objects.filter(city__region=r_compare).count()
						r_compare_count += Potential.objects.filter(city__region=r_compare).count()
				else:
					r_compare = Region.objects.filter(country=c_compare, name=imr_item.compare_name)
					if r_compare.count() > 0:
						r_compare = r_compare[0]
						r_compare_count = Mosaic.objects.filter(city__region=r_compare).count()
						r_compare_count += Potential.objects.filter(city__region=r_compare).count()
				
				region = {
					'id':imr_item.pk,
					'name':imr_item.name,
					'count':imr_item.count,
					'compare_name':imr_item.compare_name,
					'compare_count':r_compare_count,
					'mosaics':[]
				}
				
				country['regions'].append(region)
				
				if r_compare_count > 0:
					imm_results = IMMosaic.objects.filter(country_name=imc_item.name, region_name=imr_item.name)
					for imm_item in imm_results:
					
						to_add = True
						if not imm_item.compare_name:
							m_compare = Mosaic.objects.filter(city__region=r_compare, title=imm_item.name)
							if m_compare.count() > 0:
								m_compare = m_compare[0]
								imm_item.compare_name = m_compare.title
								imm_item.save()
								to_add = False
						else:
							m_compare = Mosaic.objects.filter(city__region=r_compare, title=imm_item.compare_name)
							if m_compare.count() > 0:
								m_compare = m_compare[0]
								to_add = False
						
						if to_add:
							mosaic = {
								'id':imm_item.pk,
								'name':imm_item.name,
								'count':imm_item.count,
								'country_name':imm_item.country_name,
								'region_name':imm_item.region_name,
								'city_name':imm_item.city_name,
							}
							
							region['mosaics'].append(mosaic)
		
		data['countries'].append(country)
	
	return Response(data, status=status.HTTP_200_OK)
