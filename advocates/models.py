from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta


# ---------------------------
# Admin login/activity logging
# ---------------------------
class AdminActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.login_time}"

class ActivityLog(models.Model):
    """Logs admin actions (like confirming/declining calls)."""
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.admin_user.username} - {self.action}"


# ---------------------------
# Categories & Articles
# ---------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def article_count(self):
        return self.articles.count()


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, related_name="articles", on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to="articles/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ---------------------------
# Contact Messages & Scheduled Calls
# ---------------------------
LEGAL_SERVICES = [
    ('consultancy', 'Consultancy Services'),
    ('dispute', 'Dispute Resolution'),
    ('corporate', 'Corporate & Commercial Law'),
    ('intellectual', 'Intellectual Property'),
]


class ContactMessage(models.Model):
    """Stores messages sent by clients via the contact form."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=50, choices=LEGAL_SERVICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_red_flag = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """Update red-flag status on save."""
        if not self.is_read and self.created_at <= timezone.now() - timedelta(hours=48):
            self.is_red_flag = True
        else:
            self.is_red_flag = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"


class ScheduledCall(models.Model):
    """Stores scheduled calls requested by clients."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=50, choices=LEGAL_SERVICES)
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    is_confirmed = models.BooleanField(default=False)  # Admin confirmation
    is_read = models.BooleanField(default=False)
    is_red_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """Update red-flag status on save."""
        # Ensure created_at exists before comparison
        if not self.created_at:
            super().save(*args, **kwargs)  # Save first to get created_at

        if not self.is_read and self.created_at <= timezone.now() - timedelta(hours=48):
            self.is_red_flag = True
        else:
            self.is_red_flag = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject} on {self.date} at {self.time_slot}"

    
    
class CalendarEvent(models.Model):
    # Event type choices
    MEETING = 'meeting'
    CALL = 'call'
    DEADLINE = 'deadline'
    EVENT_TYPES = [
        (MEETING, 'Meeting'),
        (CALL, 'Call'),
        (DEADLINE, 'Deadline'),
    ]

    title = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    case_name = models.CharField(max_length=200)
    date = models.DateField()
    time_slot = models.TimeField(null=True, blank=True)   # <-- Add here
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES, default=MEETING)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.event_type}) on {self.date}"

    @property
    def color(self):
        """Return color based on event type for calendar display."""
        if self.event_type == self.CALL:
            return '#10B981'
        elif self.event_type == self.DEADLINE:
            return '#EF4444'
        return '#3B82F6'
