from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from django.contrib.auth import get_user_model

LEGAL_SERVICES = [
    ('commercial', 'Commercial Practice'),
    ('dispute', 'Dispute Resolution'),
    ('consultancy', 'Consultancy Services'),
    ('debt', 'Debt Recovery'),
    ('intellectual', 'Intellectual Property'),
    ('real_estate', 'Real Estate Law'),
    ('support', 'Support Services'),
]

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
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
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

    @property
    def theme_color(self):
        """Return a CSS color class depending on whether ID is odd or even."""
        return "bg-blue-900" if self.id % 2 else "bg-amber-500"

    def __str__(self):
        return self.title


# ---------------------------
# Contact Messages & Scheduled Calls
# ---------------------------
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
        # Auto-update red flag if unread for 48h
        if self.created_at and not self.is_read and self.created_at <= timezone.now() - timedelta(hours=48):
            self.is_red_flag = True
        else:
            self.is_red_flag = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"


User = get_user_model()

class ScheduledCall(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=50, choices=LEGAL_SERVICES)
    date = models.DateField()
    time_slot = models.TimeField()
    is_confirmed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_red_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

def save(self, *args, **kwargs):
    # ✅ Skip comparison if created_at is not yet set
    if self.created_at:
        if not self.is_read and self.created_at <= timezone.now() - timedelta(hours=48):
            self.is_red_flag = True
        else:
            self.is_red_flag = False

    super().save(*args, **kwargs)

    # ✅ Automatically create CalendarEvent if confirmed and not already created
    if self.is_confirmed:
        exists = CalendarEvent.objects.filter(
            client=f"{self.first_name} {self.last_name}",
            date=self.date,
            time_slot=self.time_slot
        ).exists()

        if not exists:
            # ✅ Assign the first superuser (safe fallback)
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()  # fallback if no superuser

            CalendarEvent.objects.create(
                title=f"Call with {self.first_name} {self.last_name} at {self.time_slot.strftime('%H:%M')}",
                client=f"{self.first_name} {self.last_name}",
                case_name=self.subject,
                date=self.date,
                time_slot=self.time_slot,
                event_type=CalendarEvent.CALL,
                created_by=admin_user
            )

class CalendarEvent(models.Model):
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
    date = models.DateField(null=False, blank=False)
    time_slot = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES, default=MEETING)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.event_type}) on {self.date}"

    @property
    def color(self):
        if self.event_type == self.CALL:
            return '#10B981'
        elif self.event_type == self.DEADLINE:
            return '#EF4444'
        return '#3B82F6'

from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Message(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[('unread','Unread'), ('read','Read')], default='unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} from {self.client.name}"

class Call(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    case_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('pending','Pending'), ('completed','Completed')], default='pending')
    scheduled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Call: {self.client.name} - {self.case_name}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('message', 'Message'),
        ('call', 'Call'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    client = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    red_flag = models.BooleanField(default=False)
    # Add other fields like time_slot if needed

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='team_photos/')  # store uploaded images
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    extra_link = models.URLField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically create slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name