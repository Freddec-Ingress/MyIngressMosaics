from django.urls import reverse

from django.contrib.sitemaps import Sitemap

def ViewSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 0.5

	def items(self):
		return ['home']
	
	def location(self, item):
		return reverse(item)
