from background_task import background

from .models import *

import cloudinary
import cloudinary.uploader

from urllib.request import Request



#-------------------------------------------------------------------------------
@background(schedule=0)
def generate_previews():

	global maskimg_100
	if not maskimg_100:
		req = Request('https://www.myingressmosaics.com/static/img/mask.png', headers={'User-Agent': 'Mozilla/5.0'})
		maskfile = io.BytesIO(urllib.request.urlopen(req).read())
		maskimg_100 = Image.open(maskfile)
		size = 100, 100
		maskimg_100.thumbnail(size, Image.ANTIALIAS)
	
	global maskimg_25
	if not maskimg_25:
		req = Request('https://www.myingressmosaics.com/static/img/mask.png', headers={'User-Agent': 'Mozilla/5.0'})
		maskfile = io.BytesIO(urllib.request.urlopen(req).read())
		maskimg_25 = Image.open(maskfile)
		size = 25, 25
		maskimg_25.thumbnail(size, Image.ANTIALIAS)
		
	results = Mosaic.objects.filter(big_preview_url__isnull=True, small_preview_url__isnull=True).order_by('pk')
	if results.count() > 0:
		mosaic_obj = results[0]
	
		imgByteArr = mosaic_obj.generatePreview(100, maskimg_100)
		if imgByteArr:
			response = cloudinary.uploader.upload(imgByteArr, public_id=mosaic_obj.ref + '_100')
			mosaic_obj.big_preview_url = response['url']
	
		imgByteArr = mosaic_obj.generatePreview(25, maskimg_25)
		if imgByteArr:
			response = cloudinary.uploader.upload(imgByteArr, public_id=mosaic_obj.ref + '_25')
			mosaic_obj.small_preview_url = response['url']
		
		mosaic_obj.save()
		
		generate_previews()