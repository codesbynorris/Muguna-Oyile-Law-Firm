from .models import ContactMessage, ScheduledCall

def admin_context(request):
    """
    Makes the logged-in admin name and notification counts available on all admin pages.
    """
    if request.user.is_authenticated:
        # Red-flag messages
        red_flags = ContactMessage.objects.filter(is_red_flag=True).count()
        
        # Unread notifications (could be messages + calls)
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        unread_calls = ScheduledCall.objects.filter(is_read=False).count()
        total_notifications = unread_messages + unread_calls

        return {
            "admin_name": request.user.get_full_name() or request.user.username,
            "red_flag_count": red_flags,
            "total_notifications": total_notifications,
        }
    return {}
