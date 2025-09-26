from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import pre_save
from .models import AdminActivityLog, ActivityLog, ScheduledCall

# ---------------------------
# Admin Login Logging
# ---------------------------
@receiver(user_logged_in)
def log_admin_login(sender, request, user, **kwargs):
    if user.is_staff:  # only log admins
        AdminActivityLog.objects.create(user=user, login_time=timezone.now())

# ---------------------------
# Log call confirmations/declines automatically
# ---------------------------
@receiver(pre_save, sender=ScheduledCall)
def log_call_action(sender, instance, **kwargs):
    """
    Automatically log which admin confirmed or declined a call.
    Assumes the admin user is attached to instance._admin_user in the view.
    """
    if not instance.pk:
        # New call, do nothing
        return

    previous = ScheduledCall.objects.get(pk=instance.pk)

    if previous.is_confirmed != instance.is_confirmed:
        # Action changed, log it
        action = "confirmed" if instance.is_confirmed else "declined"

        # Admin user must be passed via a temporary attribute
        admin_user = getattr(instance, "_admin_user", None)
        if admin_user:
            ActivityLog.objects.create(
                admin_user=admin_user,
                action=f"{action.capitalize()} call: {instance.first_name} {instance.last_name} on {instance.date} at {instance.time_slot}"
            )
