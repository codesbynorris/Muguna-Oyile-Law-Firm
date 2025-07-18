from django.db import models
from django.utils.text import slugify
from django.urls import reverse


def unique_slugify(instance, value, slug_field_name='slug'):
    """
    Ensures slug is unique by appending a counter if necessary.
    """
    slug = slugify(value)
    model = type(instance)
    unique_slug = slug
    counter = 1
    while model.objects.filter(**{slug_field_name: unique_slug}).exclude(pk=instance.pk).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1
    return unique_slug


class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    ticket_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} @ {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"


# === Base Service Model Helper ===
class BaseService(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField(help_text="Short description for SEO and previews.")
    icon = models.CharField(max_length=100, blank=True, help_text='Font Awesome class, e.g., "fas fa-scale-balanced"')
    published = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=60, blank=True, help_text="Optional SEO title (overrides default).")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Optional meta description for SEO.")

    class Meta:
        abstract = True
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# === Consultancy ===
class ConsultancyService(BaseService):
    def get_absolute_url(self):
        return reverse("consultancy_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Consultancy Service"
        verbose_name_plural = "Consultancy Services"


class ConsultancyDetail(models.Model):
    consultancy_service = models.ForeignKey(ConsultancyService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text


# === Corporate ===
class CorporateService(BaseService):
    def get_absolute_url(self):
        return reverse("corporate_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Corporate Service"
        verbose_name_plural = "Corporate Services"


class CorporateDetail(models.Model):
    corporate_service = models.ForeignKey(CorporateService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text


# === Dispute Resolution ===
class DisputeService(BaseService):
    def get_absolute_url(self):
        return reverse("dispute_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Dispute Resolution Service"
        verbose_name_plural = "Dispute Resolution Services"


class DisputeDetail(models.Model):
    dispute_service = models.ForeignKey(DisputeService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text


# === Property Law ===
class PropertyService(BaseService):
    def get_absolute_url(self):
        return reverse("property_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Property Law Service"
        verbose_name_plural = "Property Law Services"


class PropertyDetail(models.Model):
    property_service = models.ForeignKey(PropertyService, related_name='details', on_delete=models.CASCADE)
    detail_text = models.CharField(max_length=255)

    def __str__(self):
        return self.detail_text
