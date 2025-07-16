# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'about',
            'services',
            'team',
            'contact',
            'privacy_policy',
            'terms_of_service',
            'consultancy',
            'corporate',
            'dispute_resolution',
            'property',
        ]

    def location(self, item):
        return reverse(item)
