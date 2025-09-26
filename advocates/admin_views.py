from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from .models import ContactMessage, ScheduledCall, AdminActivityLog
from advocates.models import ActivityLog

# ---------------------------
# Helpers
# ---------------------------
def admin_required(user):
    return user.is_staff

def send_html_email(subject, template, context, to_email):
    html_content = render_to_string(template, context)
    text_content = render_to_string(template, context).replace("<br>", "\n")
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


# ---------------------------
# Dashboard Home
# ---------------------------
@login_required
@user_passes_test(admin_required)
def dashboard_home(request):
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    pending_calls = ScheduledCall.objects.filter(is_confirmed=False).count()
    red_flag_count = ContactMessage.objects.filter(is_red_flag=True).count()
    total_notifications = unread_messages + pending_calls
    recent_activity = ActivityLog.objects.order_by("-created_at")[:10]

    context = {
        "admin_name": request.user.get_full_name() or request.user.username,
        "unread_messages": unread_messages,
        "pending_calls": pending_calls,
        "red_flag_count": red_flag_count,
        "total_notifications": total_notifications,
        "recent_activity": recent_activity,
    }
    return render(request, "admin_dashboard/dashboard.html", context)


# ---------------------------
# Contacts
# ---------------------------
@login_required
@user_passes_test(admin_required)
def contacts_list(request):
    contacts = ContactMessage.objects.order_by("-created_at")
    return render(request, "admin_dashboard/contacts.html", {"contacts": contacts})


# ---------------------------
# Scheduled Calls
# ---------------------------
@login_required
@user_passes_test(admin_required)
def scheduled_calls_list(request):
    calls = ScheduledCall.objects.order_by("-date", "-time_slot")
    return render(request, "admin_dashboard/scheduled_calls.html", {"calls": calls})


# ---------------------------
# Activity Logs
# ---------------------------
@login_required
@user_passes_test(admin_required)
def activity_log_list(request):
    logs = ActivityLog.objects.order_by("-created_at")
    return render(request, "admin_dashboard/activity_log.html", {"logs": logs})


# ---------------------------
# Confirm Call
# ---------------------------
@login_required
@user_passes_test(admin_required)
def confirm_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)
    call.is_confirmed = True
    call.save()

    send_html_email(
        subject="✅ Your call has been confirmed",
        template="emails/call_confirmed.html",
        context={"call": call, "firm_name": "Law Firm"},
        to_email=call.email,
    )

    ActivityLog.objects.create(
        admin_user=request.user,
        action=f"Confirmed call for {call.first_name} {call.last_name} on {call.date} at {call.time_slot}",
    )

    messages.success(request, f"Call with {call.first_name} confirmed.")
    return redirect("admin_dashboard_calls")


# ---------------------------
# Decline Call
# ---------------------------
@login_required
@user_passes_test(admin_required)
def decline_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)

    send_html_email(
        subject="❌ Your call has been declined",
        template="emails/call_declined.html",
        context={"call": call, "firm_name": "Law Firm"},
        to_email=call.email,
    )

    ActivityLog.objects.create(
        admin_user=request.user,
        action=f"Declined call for {call.first_name} {call.last_name} on {call.date} at {call.time_slot}",
    )

    call.delete()
    messages.success(request, f"Call with {call.first_name} declined.")
    return redirect("admin_dashboard_calls")


# ---------------------------
# Red-Flag Messages
# ---------------------------
@login_required
@user_passes_test(admin_required)
def red_flag_messages(request):
    flagged = ContactMessage.objects.filter(is_red_flag=True).order_by('-created_at')
    return render(request, "admin_dashboard/red_flag_messages.html", {"red_flags": flagged})


# ---------------------------
# Fetch Notifications (AJAX)
# ---------------------------
@login_required
@user_passes_test(admin_required)
def fetch_notifications(request):
    messages_qs = ContactMessage.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).order_by('-created_at')[:10]
    calls_qs = ScheduledCall.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).order_by('-created_at')[:10]

    notifications = []
    for m in messages_qs:
        notifications.append({
            "type": "message",
            "client": f"{m.first_name} {m.last_name}",
            "subject": m.subject,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    for c in calls_qs:
        notifications.append({
            "type": "call",
            "client": f"{c.first_name} {c.last_name}",
            "subject": f"Call on {c.date} at {c.time_slot}",
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    notifications.sort(key=lambda n: n["created_at"], reverse=True)
    return JsonResponse({"notifications": notifications[:10]})


# ---------------------------
# All Notifications Page
# ---------------------------
@login_required
@user_passes_test(admin_required)
def all_notifications(request):
    # Only unread messages
    messages_qs = ContactMessage.objects.filter(is_read=False).order_by('-created_at')
    # Only unconfirmed calls
    calls_qs = ScheduledCall.objects.filter(is_confirmed=False).order_by('-created_at')

    notifications = []

    for msg in messages_qs:
        notifications.append({
            "type": "message",
            "client": f"{msg.first_name} {msg.last_name}",
            "subject": msg.subject,
            "created_at": msg.created_at,
        })

    for call in calls_qs:
        notifications.append({
            "type": "call",
            "client": f"{call.first_name} {call.last_name}",
            "subject": f"Call on {call.date} at {call.time_slot}",
            "created_at": call.created_at,
        })

    # sort by created_at descending
    notifications.sort(key=lambda x: x["created_at"], reverse=True)

    return render(request, "admin_dashboard/all_notifications.html", {
        "notifications": notifications
    })



# ---------------------------
# Red-Flag Notifications (AJAX for red dot)
# ---------------------------
@login_required
@user_passes_test(admin_required)
def fetch_red_flag_notifications(request):
    now = timezone.now()
    red_flags = []

    overdue_messages = ContactMessage.objects.filter(
        is_read=False, created_at__lte=now - timedelta(hours=48)
    )
    overdue_calls = ScheduledCall.objects.filter(
        is_read=False, created_at__lte=now - timedelta(hours=48)
    )

    for msg in overdue_messages:
        red_flags.append({
            "id": msg.id,
            "type": "message",
            "subject": msg.subject,
            "client": f"{msg.first_name} {msg.last_name}",
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    for call in overdue_calls:
        red_flags.append({
            "id": call.id,
            "type": "call",
            "subject": call.subject,
            "client": f"{call.first_name} {call.last_name}",
            "date": str(call.date),
            "time_slot": call.time_slot,
            "created_at": call.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    red_flags = sorted(red_flags, key=lambda x: x["created_at"], reverse=True)
    return JsonResponse({"red_flags": red_flags})
