from django.db import models
<<<<<<< HEAD
=======
from django.utils.text import slugify
>>>>>>> aec289d (SEO start)

# Create your models here.

class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    ticket_id = models.CharField(max_length=50, unique=True, blank=True, null=True)  
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} @ {self.submitted_at:%Y-%m-%d %H:%M}"
<<<<<<< HEAD
=======

class ConsultancyService(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    summary = models.TextField()
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ConsultancyDetail(models.Model):
    consultancy_service = models.ForeignKey(ConsultancyService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text
    
class CorporateService(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CorporateDetail(models.Model):
    corporate_service = models.ForeignKey(CorporateService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text

class DisputeService(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField()
    icon = models.CharField(max_length=100, help_text='Font Awesome class, e.g., "fas fa-balance-scale"')
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class DisputeDetail(models.Model):
    dispute_service = models.ForeignKey(DisputeService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text
    
class PropertyService(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField()
    icon = models.CharField(max_length=100)
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PropertyDetail(models.Model):
    property_service = models.ForeignKey(PropertyService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text
>>>>>>> aec289d (SEO start)
