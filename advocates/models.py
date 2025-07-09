from django.db import models

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
