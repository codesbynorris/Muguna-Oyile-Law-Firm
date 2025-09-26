from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localdate
import json


from .forms import ContactMessageForm, ScheduledCallForm
from .models import (
    ContactMessage,
    ScheduledCall,
    Category,
    Article,
    AdminActivityLog,
    ActivityLog,
    CalendarEvent,
)

# ---------------------------
# Helpers
# ---------------------------
def send_html_email(subject, template, context, to_email):
    """Send HTML email with plain text fallback."""
    html_content = render_to_string(template, context)
    text_content = render_to_string(template, context).replace('<br>', '\n')

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def admin_check(user):
    """Check if user is admin/staff."""
    return user.is_staff

def send_today_event_notifications():
    today = localdate()
    events_today = CalendarEvent.objects.filter(date=today)
    
    for event in events_today:
        # Send email to admin
        send_html_email(
            subject=f"🔔 Event Today: {event.title}",
            template="emails/event_reminder_admin.html",
            context={"event": event, "firm_name": "Law Firm"},
            to_email=settings.CONTACT_RECEIVER_EMAIL,
        )

        # Send email to client if email exists
        if hasattr(event, "client_email") and event.client_email:
            send_html_email(
                subject=f"🔔 Reminder: Your event today - {event.title}",
                template="emails/event_reminder_client.html",
                context={"event": event, "firm_name": "Law Firm"},
                to_email=event.client_email,
            )

# ---------------------------
# General Pages
# ---------------------------
def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def team(request):
    return render(request, "team.html")


def privacy_policy(request):
    return render(request, "T&C/privacypolicy.html")


def terms_of_service(request):
    return render(request, "T&C/termsofservice.html")


# ---------------------------
# Service Pages
# ---------------------------
def intellectual_property(request):
    return render(request, "services/intellectual_property.html")


def dispute_resolution(request):
    return render(request, "services/dispute_resolution.html")


def debt_management(request):
    return render(request, "services/debt_management.html")


def commercial_practice(request):
    return render(request, "services/commercial_practice.html")


def real_estate_leases(request):
    return render(request, "services/real_estate_leases.html")


def support_services(request):
    return render(request, "services/support_services.html")


# ---------------------------
# Articles
# ---------------------------
def article_list(request, category_slug=None):
    categories = Category.objects.all()
    articles = Article.objects.all()
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)

    context = {
        "articles": articles,
        "categories": categories,
        "active_category": category,
    }
    return render(request, "articles/article_list.html", context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    categories = Category.objects.all()
    context = {
        "article": article,
        "categories": categories,
    }
    return render(request, "articles/article_detail.html", context)


# ---------------------------
# Contact & Schedule Call
# ---------------------------
def contact_us(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # --- Contact Message ---
        if form_type == "message":
            form = ContactMessageForm(request.POST)
            if form.is_valid():
                contact = form.save()

                # Email to admin
                send_html_email(
                    subject=f"📩 New Contact Message - {contact.subject}",
                    template="emails/contact_admin.html",
                    context={"contact": contact, "firm_name": "Law Firm"},
                    to_email=settings.CONTACT_RECEIVER_EMAIL,
                )

                # Email to user
                send_html_email(
                    subject="✅ We received your message",
                    template="emails/contact_user.html",
                    context={"contact": contact, "firm_name": "Law Firm"},
                    to_email=contact.email,
                )

                messages.success(request, "Your message has been sent successfully!")
                return redirect("contact")

        # --- Schedule a Call ---
        elif form_type == "schedule":
            form = ScheduledCallForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data["date"]
                time_slot = form.cleaned_data["time_slot"]

                if ScheduledCall.objects.filter(date=date, time_slot=time_slot).exists():
                    messages.error(request, "This slot is already booked. Please choose another.")
                else:
                    call = form.save()

                    # Email to admin
                    send_html_email(
                        subject=f"📅 New Call Request - {call.first_name} {call.last_name}",
                        template="emails/call_admin.html",
                        context={"call": call, "firm_name": "Law Firm"},
                        to_email=settings.CONTACT_RECEIVER_EMAIL,
                    )

                    # Email to user
                    send_html_email(
                        subject="⏳ Call request received",
                        template="emails/call_user.html",
                        context={"call": call, "firm_name": "Law Firm"},
                        to_email=call.email,
                    )

                    messages.success(request, "Your call request has been submitted!")
                    return redirect("contact")
    else:
        form = ContactMessageForm()

    return render(request, "contact.html", {"form": form})


# ---------------------------
# Admin Dashboard
# ---------------------------
@login_required
@user_passes_test(admin_check)
def admin_dashboard(request):
    user = request.user

    # Dashboard Cards
    total_clients = ContactMessage.objects.count()
    active_cases = ScheduledCall.objects.filter(is_confirmed=True).count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    unread_calls = ScheduledCall.objects.filter(is_read=False).count()

    # Recent Activity
    recent_messages = ContactMessage.objects.order_by("-created_at")[:5]
    recent_calls = ScheduledCall.objects.order_by("-created_at")[:5]
    recent_activity = ActivityLog.objects.order_by("-created_at")[:10]
    active_events = CalendarEvent.objects.filter(date__gte=localdate()).order_by('date')

    # Highlight red flags: queries not replied in 48h
    now = timezone.now()
    overdue_messages = ContactMessage.objects.filter(
        is_read=False, created_at__lte=now - timedelta(hours=48)
    )
    overdue_calls = ScheduledCall.objects.filter(
        is_read=False, created_at__lte=now - timedelta(hours=48)
    )

    for msg in overdue_messages:
        msg.is_red_flag = True
    for call in overdue_calls:
        call.is_red_flag = True

    # Recent logins
    recent_logins = AdminActivityLog.objects.order_by("-login_time")[:10]

    # ----------------------------
    # Point 4: Send notifications for today's events
    # ----------------------------
    today = localdate()
    events_today = CalendarEvent.objects.filter(date=today)
    for event in events_today:
        # Email to admin
        send_html_email(
            subject=f"🔔 Event Today: {event.title}",
            template="emails/event_reminder_admin.html",
            context={"event": event, "firm_name": "Law Firm"},
            to_email=settings.CONTACT_RECEIVER_EMAIL,
        )
        # Email to client if available
        if hasattr(event, "client_email") and event.client_email:
            send_html_email(
                subject=f"🔔 Reminder: Your event today - {event.title}",
                template="emails/event_reminder_client.html",
                context={"event": event, "firm_name": "Law Firm"},
                to_email=event.client_email,
            )

    context = {
        "user": user,
        "total_clients": total_clients,
        "active_cases": active_cases,
        "unread_messages": unread_messages,
        "unread_calls": unread_calls,
        "recent_messages": recent_messages,
        "recent_calls": recent_calls,
        "recent_activity": recent_activity,
        "recent_logins": recent_logins,
        "overdue_messages": overdue_messages,
        "overdue_calls": overdue_calls,
        "active_events": active_events,
    }
    return render(request, "admin_dashboard/dashboard.html", context)


# ---------------------------
# Fetch Notifications (AJAX)
# ---------------------------
@login_required
@user_passes_test(admin_check)
def fetch_notifications(request):
    now = timezone.now()
    notifications = []

    unread_msgs = ContactMessage.objects.filter(is_read=False).order_by("-created_at")
    unread_calls = ScheduledCall.objects.filter(is_read=False).order_by("-created_at")

    for msg in unread_msgs:
        notifications.append({
            "id": msg.id,
            "type": "message",
            "subject": msg.subject,
            "client": f"{msg.first_name} {msg.last_name}" if hasattr(msg, "first_name") else "",
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M"),
            "red_flag": msg.created_at <= now - timedelta(hours=48)
        })

    for call in unread_calls:
        notifications.append({
            "id": call.id,
            "type": "call",
            "client": f"{call.first_name} {call.last_name}",
            "time_slot": call.time_slot.strftime("%H:%M") if call.time_slot else "",
            "created_at": call.created_at.strftime("%Y-%m-%d %H:%M"),
            "red_flag": call.created_at <= now - timedelta(hours=48)
        })

    notifications = sorted(notifications, key=lambda x: x["created_at"], reverse=True)
    return JsonResponse({"notifications": notifications})


# ---------------------------
# Admin Actions for Calls
# ---------------------------
@login_required
@user_passes_test(admin_check)
def confirm_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)
    call.is_confirmed = True
    call.is_read = True
    call._admin_user = request.user
    call.save()

    # Create CalendarEvent automatically (includes time)
    title_with_time = f"Call with {call.first_name} {call.last_name} at {call.time_slot.strftime('%H:%M')}"
    CalendarEvent.objects.create(
        title=title_with_time,
        client=f"{call.first_name} {call.last_name}",
        case_name=call.subject,
        date=call.date,
        event_type=CalendarEvent.CALL,
        created_by=request.user,
        time_slot=call.time_slot
    )

    # Log admin activity
    ActivityLog.objects.create(
        admin_user=request.user,
        action=f"Confirmed call: {call.first_name} {call.last_name} at {call.time_slot.strftime('%H:%M')}"
    )

    # Email notifications
    send_html_email(
        subject="✅ Your call has been confirmed",
        template="emails/call_confirmed.html",
        context={
            "call": call,
            "firm_name": "Law Firm",
            "booking_link": "https://yourfirm.com/schedule-call",
        },
        to_email=call.email,
    )

    messages.success(request, f"Call with {call.first_name} confirmed and added to calendar.")
    return redirect("admin_dashboard")




@login_required
@user_passes_test(admin_check)
def decline_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)
    call.is_confirmed = False
    call.is_read = True
    call._admin_user = request.user
    call.save()

    send_html_email(
        subject="❌ Your call request was declined",
        template="emails/call_declined.html",
        context={
            "call": call,
            "firm_name": "Law Firm",
            "booking_link": "https://yourfirm.com/schedule-call",
        },
        to_email=call.email,
    )

    messages.success(request, f"Call with {call.first_name} declined. User notified.")
    return redirect("admin_dashboard")


@login_required
@user_passes_test(lambda u: u.is_staff)
def all_notifications(request):
    messages_list = ContactMessage.objects.all().order_by("-created_at")
    calls_list = ScheduledCall.objects.all().order_by("-created_at")
    red_flags = AdminActivityLog.objects.all().order_by("-created_at")

    context = {
        "messages": messages_list,
        "calls": calls_list,
        "red_flags": red_flags,
    }
    return render(request, "admin_dashboard/all_notifications.html", context)


# ---------------------------
# Internal Calendar Events
# ---------------------------
@login_required
def fetch_events(request):
    data = []

    # CalendarEvent
    for e in CalendarEvent.objects.all():
        start_iso = e.date.isoformat()
        if getattr(e, 'time_slot', None):
            start_iso += f"T{e.time_slot.strftime('%H:%M:%S')}"
        data.append({
            "id": e.id,
            "title": e.title,
            "start": start_iso,
            "color": e.color or "#2563EB",
        })

    # Confirmed ScheduledCalls without CalendarEvent
    confirmed_calls = ScheduledCall.objects.filter(is_confirmed=True)
    for call in confirmed_calls:
        # Skip if CalendarEvent already exists
        if not CalendarEvent.objects.filter(
            client=f"{call.first_name} {call.last_name}",
            date=call.date,
            time_slot=call.time_slot
        ).exists():
            start_iso = call.date.isoformat() + f"T{call.time_slot.strftime('%H:%M:%S')}"
            data.append({
                "id": f"call-{call.id}",
                "title": f"Call with {call.first_name} {call.last_name} at {call.time_slot.strftime('%H:%M')}",
                "start": start_iso,
                "color": "#10B981"
            })

    return JsonResponse(data, safe=False)



       



@csrf_exempt
@login_required
def add_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        client = data.get('client')
        case_name = data.get('case_name')
        date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        event_type = data.get('event_type')

        event = CalendarEvent.objects.create(
            title=title,
            client=client,
            case_name=case_name,
            date=date,
            event_type=event_type,
            created_by=request.user
        )

        return JsonResponse({
            "id": event.id,
            "title": event.title,
            "start": event.date.isoformat(),
            "color": event.color
        })


@csrf_exempt
@login_required
def delete_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(CalendarEvent, id=event_id)
        event.delete()
        return JsonResponse({"success": True})


@csrf_exempt
@login_required
def edit_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(CalendarEvent, id=event_id)
        data = json.loads(request.body)
        event.title = data.get('title', event.title)
        event.save()
        return JsonResponse({"title": event.title})
