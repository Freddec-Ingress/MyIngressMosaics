from django.contrib.sitemaps import Sitemap

def ViewSitemap(Sitemap):
	changefreq = "never"
	priority = 0.5

	def items(self):
		return ['main', 'about', 'license']
	
	def location(self, item):
		return reverse(item)
