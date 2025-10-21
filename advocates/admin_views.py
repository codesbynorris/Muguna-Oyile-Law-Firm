from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from datetime import timedelta, datetime
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import Feedback, Notification

from advocates.forms import ArticleForm, ContactMessageForm, ScheduledCallForm
from .models import (
    LEGAL_SERVICES,
    Article,
    ContactMessage,
    ScheduledCall,
    AdminActivityLog,
    ActivityLog,
    CalendarEvent,
    Message,
    Call,   
    Client, 
)
from advocates.models import Category

# ---------------------------
# Helpers
# ---------------------------
def admin_required(user):
    return user.is_staff or user.is_superuser

def send_html_email(subject, template, context, to_email):
    try:
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
    except Exception as e:
        print(f"Email sending failed to {to_email}: {e}")

# ---------------------------
# Admin Dashboard
# ---------------------------
# In advocates/views.py

@login_required
@user_passes_test(admin_required)
def dashboard_home(request):
    now = timezone.now()
    
    # 1. Update Red Flags (This is essential for real-time counting)
    ContactMessage.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)
    ScheduledCall.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)

    # 2. Fetch Metrics (The counts you see on the dashboard cards)
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    pending_calls = ScheduledCall.objects.filter(is_confirmed=False).count()
    red_flag_count = ContactMessage.objects.filter(is_red_flag=True).count() + \
                     ScheduledCall.objects.filter(is_red_flag=True).count()
    total_notifications = unread_messages + pending_calls

    # 3. Fetch Dynamic Content
    recent_activity = ActivityLog.objects.order_by("-created_at")[:10]
    
    # FIXED: Fetch Upcoming Appointments (Confirmed Events)
    # The date__isnull=False filter ensures we only query records that have a date,
    # preventing the 'NoneType' error in the template when applying the |date filter.
    upcoming_events = CalendarEvent.objects.filter(
        date__gte=now.date(),
        date__isnull=False
    ).order_by('date', 'time_slot')[:5]

    latest_messages = ContactMessage.objects.order_by('-created_at')[:10]
    latest_calls = ScheduledCall.objects.order_by('-created_at')[:10]

    context = {
        "admin_name": request.user.get_full_name() or request.user.username,
        "unread_messages": unread_messages,
        "pending_calls": pending_calls,
        "red_flag_count": red_flag_count,
        "total_notifications": total_notifications,
        "recent_activity": recent_activity,
        "upcoming_events": upcoming_events, 
        
        # Ensure these are correctly handled or removed if not used elsewhere
        "total_clients": 0, # Placeholder/Replace with actual query if needed
        "active_cases": 0,  # Placeholder/Replace with actual query if needed
    }
    return render(request, "admin_dashboard/dashboard.html", context)


# ---------------------------
# Contact & Schedule Call
# ---------------------------
@login_required
@user_passes_test(admin_required)
def contacts_list(request):
    contacts = ContactMessage.objects.all().order_by('-created_at')
    calls = ScheduledCall.objects.all().order_by('-created_at')
    return render(request, "admin_dashboard/contacts_list.html", {
        "contacts": contacts,
        "calls": calls,
    })
# ---------------------------
# Confirm & Decline Calls
# ---------------------------
@login_required
@user_passes_test(admin_required)
def confirm_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)
    call.is_confirmed = True
    call.is_read = True
    call.save()

    # Auto-create CalendarEvent if none exists
    if not hasattr(call, "calendar_event") or not call.calendar_event:
        event_title = f"Call with {call.first_name} {call.last_name} at {call.time_slot.strftime('%H:%M')}"
        event = CalendarEvent.objects.create(
            title=event_title,
            client=f"{call.first_name} {call.last_name}",
            case_name=call.subject,
            date=call.date,
            time_slot=call.time_slot,
            event_type=CalendarEvent.CALL,
            created_by=request.user,
        )
        call.calendar_event = event
        call.save()

    # Log admin activity
    ActivityLog.objects.create(
        admin_user=request.user,
        action=f"Confirmed call for {call.first_name} {call.last_name} on {call.date} at {call.time_slot}",
    )

    # Email notifications
    send_html_email(
        subject="✅ Your call has been confirmed",
        template="emails/call_confirmed.html",
        context={"call": call, "firm_name": "Law Firm"},
        to_email=call.email,
    )

    messages.success(request, f"Call with {call.first_name} confirmed and added to calendar.")
    return redirect("admin_dashboard_calls")


@login_required
@user_passes_test(admin_required)
def decline_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)

    # Email notification
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
# Notifications (AJAX)
# ---------------------------
@login_required
@user_passes_test(admin_required)
def fetch_notifications(request):
    now = timezone.now()
    notifications = []

    # 1. Update red flags dynamically (keep this as is)
    ContactMessage.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)
    ScheduledCall.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)

    # 2. Filter Contact Messages (FIXED)
    # Exclude records where created_at is null before iterating
    for msg in ContactMessage.objects.filter(is_read=False, created_at__isnull=False).order_by("-created_at"):
        notifications.append({
            "id": msg.id,
            "type": "message",
            "subject": msg.subject,
            "client": f"{msg.first_name} {msg.last_name}",
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M"),
            "red_flag": msg.is_red_flag
        })

    # 3. Filter Scheduled Calls (FIXED)
    # Exclude records where created_at is null before iterating
    for call in ScheduledCall.objects.filter(is_read=False, created_at__isnull=False).order_by("-created_at"):
        notifications.append({
            "id": call.id,
            "type": "call",
            "client": f"{call.first_name} {call.last_name}",
            # Note: time_slot is a TimeField, which might also be null.
            # You should check if time_slot is null on the model, 
            # but created_at is the main problem.
            "time_slot": call.time_slot.strftime("%H:%M") if call.time_slot else None,
            "created_at": call.created_at.strftime("%Y-%m-%d %H:%M"),
            "red_flag": call.is_red_flag
        })

    notifications = sorted(notifications, key=lambda x: x["created_at"], reverse=True)
    return JsonResponse({"notifications": notifications})
# ---------------------------
# Article Management
# ---------------------------
@login_required
@user_passes_test(admin_required)
def article_create(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            return JsonResponse({"success": True, "message": f"Article '{article.title}' published successfully!"})
        else:
            errors = {field: [{"message": str(e)} for e in field_errors] for field, field_errors in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors})

    form = ArticleForm()
    return render(request, "admin_dashboard/article_create.html", {"form": form})

@login_required
@user_passes_test(admin_required)
def manage_blogs(request):
    blogs = Article.objects.all()
    category_filter = request.GET.get('category', '')
    author_filter = request.GET.get('author', '')

    if category_filter:
        blogs = blogs.filter(category__name__iexact=category_filter)
    if author_filter:
        blogs = blogs.filter(author__iexact=author_filter)

    authors = Article.objects.values_list('author', flat=True).distinct()
    categories = [c[1] for c in LEGAL_SERVICES]

    return render(request, 'admin_dashboard/manage_blogs.html', {
        'blogs': blogs,
        'authors': authors,
        'categories': categories,
        'selected_category': category_filter,
        'selected_author': author_filter,
    })

@login_required
@user_passes_test(admin_required)
def view_blog(request, blog_id):
    article = get_object_or_404(Article, id=blog_id)
    return render(request, 'admin_dashboard/view_blog.html', {'article': article})

@login_required
@user_passes_test(admin_required)
def edit_blog(request, blog_id):
    article = get_object_or_404(Article, id=blog_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully.")
            return redirect('manage_blogs')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'admin_dashboard/edit_blog.html', {'form': form, 'article': article})

@login_required
@user_passes_test(admin_required)
def delete_blog(request, blog_id):
    article = get_object_or_404(Article, id=blog_id)
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect('manage_blogs')
    return render(request, 'admin_dashboard/delete_blog.html', {'article': article})

# ---------------------------
# Admin Profile & Logout
# ---------------------------
@login_required
def admin_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully.')

        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
        elif request.POST.get('old_password'):
            messages.error(request, 'Password change failed. Check the old password.')

        return redirect('admin_profile')

    return render(request, 'admin_dashboard/admin_profile.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(admin_required)
def scheduled_calls_admin(request):
    calls = ScheduledCall.objects.order_by('-date', '-time_slot')
    return render(request, "admin_dashboard/scheduled_calls.html", {"calls": calls})

@login_required
@user_passes_test(admin_required)
def activity_log_list(request):
    activities = ActivityLog.objects.order_by('-created_at')
    return render(request, "admin_dashboard/activity_log_list.html", {"activities": activities})

@login_required
@user_passes_test(admin_required)
def red_flag_messages(request):
    messages = ContactMessage.objects.filter(is_red_flag=True).order_by('-created_at')
    calls = ScheduledCall.objects.filter(is_red_flag=True).order_by('-created_at')
    
    return render(
        request,
        "admin_dashboard/red_flag_messages.html",
        {
            "messages": messages,
            "calls": calls,
        }
    )

@csrf_exempt
def add_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        client, _ = Client.objects.get_or_create(name=data['client'], email=data.get('email',''))
        message = Message.objects.create(
            client=client,
            subject=data['subject'],
            content=data['content']
        )

        # Send email notification
        send_mail(
            subject=f"New Message: {message.subject}",
            message=f"From: {client.name}\n\n{message.content}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        return JsonResponse({
            "id": message.id,
            "client": client.name,
            "subject": message.subject,
            "status": message.status
        })


@csrf_exempt
def add_call(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        client, _ = Client.objects.get_or_create(name=data['client'], email=data.get('email',''))
        call = Call.objects.create(
            client=client,
            case_name=data['case_name'],
            scheduled_at=data['scheduled_at']
        )

        # Send email notification
        send_mail(
            subject=f"New Call Scheduled: {call.case_name}",
            message=f"Client: {client.name}\nCase: {call.case_name}\nScheduled at: {call.scheduled_at}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        return JsonResponse({
            "id": call.id,
            "client": client.name,
            "case_name": call.case_name,
            "status": call.status
        })
    
    from .models import Message, Call

def admin_dashboard(request):
    unread_messages = Message.objects.filter(status='unread').count()
    pending_calls = Call.objects.filter(status='pending').count()
    total_clients = Client.objects.count()
    active_cases = Call.objects.filter(status='pending').count()  # Or another criteria

    recent_activity = []  # Fetch logs if you have an ActivityLog model

    return render(request, 'admin_dashboard/dashboard.html', {
        'unread_messages': unread_messages,
        'pending_calls': pending_calls,
        'total_clients': total_clients,
        'active_cases': active_cases,
        'recent_activity': recent_activity
    })

from .models import Notification  # make sure to import Notification

@login_required
@user_passes_test(admin_required)
def contact_view(request):
    contact_form = ContactMessageForm()
    call_form = ScheduledCallForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # ---------------------------
        # Contact Message Form
        # ---------------------------
        if form_type == "message":
            contact_form = ContactMessageForm(request.POST)
            if contact_form.is_valid():
                try:
                    contact = contact_form.save(commit=False)
                    contact.is_read = False
                    contact.is_red_flag = False
                    contact.save()

                    # Auto red flag if older than 48h
                    if contact.created_at <= timezone.now() - timedelta(hours=48):
                        contact.is_red_flag = True
                        contact.save()

                    # CREATE NOTIFICATION
                    Notification.objects.create(
                        title=f"New message from {contact.first_name} {contact.last_name}",
                        type="message",
                        related_id=contact.id,  # optional, depends on your Notification model
                    )

                    # Email to admin
                    send_html_email(
                        subject=f"📩 New Contact Message - {contact.subject}",
                        template="emails/contact_admin.html",
                        context={"contact": contact, "firm_name": "Law Firm"},
                        to_email=settings.CONTACT_RECEIVER_EMAIL,
                    )

                    # Email to client
                    send_html_email(
                        subject="✅ We received your message",
                        template="emails/contact_user.html",
                        context={"contact": contact, "firm_name": "Law Firm"},
                        to_email=contact.email,
                    )

                    messages.success(request, "Your message has been sent successfully!")
                    return redirect("/contact/?sent=1")

                except Exception as e:
                    messages.error(request, f"Failed to send message: {str(e)}")
                    return redirect("/contact/?sent=0")

        # ---------------------------
        # Schedule Call Form
        # ---------------------------
        elif form_type == "schedule":
            call_form = ScheduledCallForm(request.POST)
            if call_form.is_valid():
                try:
                    date = call_form.cleaned_data["date"]
                    time_slot = call_form.cleaned_data["time_slot"]

                    # Prevent double booking
                    if ScheduledCall.objects.filter(date=date, time_slot=time_slot).exists():
                        messages.error(request, "This slot is already booked. Please choose another.")
                        return redirect("/contact/?sent=0")

                    call = call_form.save(commit=False)
                    call.is_read = False
                    call.is_red_flag = False
                    call.is_confirmed = False
                    call.save()

                    # Auto red flag if older than 48h
                    if call.created_at <= timezone.now() - timedelta(hours=48):
                        call.is_red_flag = True
                        call.save()

                    # CREATE NOTIFICATION
                    Notification.objects.create(
                        title=f"New scheduled call from {call.first_name} {call.last_name}",
                        type="schedule",
                        related_id=call.id,
                    )

                    # Email to admin
                    send_html_email(
                        subject=f"📅 New Call Request - {call.first_name} {call.last_name}",
                        template="emails/call_admin.html",
                        context={"call": call, "firm_name": "Law Firm"},
                        to_email=settings.CONTACT_RECEIVER_EMAIL,
                    )

                    # Email to client
                    send_html_email(
                        subject="⏳ Call request received",
                        template="emails/call_user.html",
                        context={"call": call, "firm_name": "Law Firm"},
                        to_email=call.email,
                    )

                    messages.success(request, "Your call request has been submitted!")
                    return redirect("/contact/?sent=1")

                except Exception as e:
                    messages.error(request, f"Failed to schedule call: {str(e)}")
                    return redirect("/contact/?sent=0")

    return render(
        request,
        "contact.html",
        {
            "contact_form": contact_form,
            "call_form": call_form,
            "legal_services": LEGAL_SERVICES,
            "status": request.GET.get("sent"),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def all_notifications(request):
    now = timezone.now()
    notifications = []

    # Update red flags for unread items older than 48h
    ContactMessage.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)
    ScheduledCall.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)

    # Contact Messages
    for msg in ContactMessage.objects.all().order_by('-created_at'):
        notifications.append({
            "type": "message",
            "client": f"{msg.first_name} {msg.last_name}",
            "subject": msg.subject,
            "created_at": msg.created_at,
            "red_flag": msg.is_red_flag,
        })

    # Scheduled Calls
    for call in ScheduledCall.objects.all().order_by('-created_at'):
        notifications.append({
            "type": "call",
            "client": f"{call.first_name} {call.last_name}",
            "subject": getattr(call, "subject", "Call"),
            "created_at": call.created_at,
            "red_flag": call.is_red_flag,
        })

    # Sort by newest first
    notifications.sort(key=lambda x: x["created_at"], reverse=True)

    return render(request, 'admin_dashboard/all_notifications.html', {
        'notifications': notifications
    })

def test_email(request):
    try:
        send_mail(
            subject='Test Email',
            message='This is a test email from Django.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=False,
        )
        return HttpResponse('Email sent successfully!')
    except Exception as e:
        return HttpResponse(f'Error sending email: {str(e)}')

@login_required
@staff_member_required
def feedback_dashboard(request):
    selected_type = request.GET.get('type', 'all')

    if selected_type == 'all':
        feedbacks = Feedback.objects.all().order_by('-submitted_at')
    else:
        feedbacks = Feedback.objects.filter(feedback_type__iexact=selected_type).order_by('-submitted_at')

    print(f"Retrieved feedbacks: {feedbacks.count()} for type={selected_type}")
    return render(request, 'admin_dashboard/feedback_admin.html', {
        'feedbacks': feedbacks,
        'selected_type': selected_type,
    })
