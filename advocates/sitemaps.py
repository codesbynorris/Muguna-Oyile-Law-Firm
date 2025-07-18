# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from advocates.models import (
    ConsultancyService,
    CorporateService,
    DisputeService,
    PropertyService
)

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


class ConsultancySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return ConsultancyService.objects.filter(published=True)

    def location(self, obj):
        return reverse('consultancy_service_detail', kwargs={'slug': obj.slug})


class CorporateSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return CorporateService.objects.filter(published=True)

    def location(self, obj):
        return reverse('corporate_service_detail', kwargs={'slug': obj.slug})


class DisputeSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return DisputeService.objects.filter(published=True)

    def location(self, obj):
        return reverse('dispute_service_detail', kwargs={'slug': obj.slug})


class PropertySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return PropertyService.objects.filter(published=True)

    def location(self, obj):
        return reverse('property_service_detail', kwargs={'slug': obj.slug})
