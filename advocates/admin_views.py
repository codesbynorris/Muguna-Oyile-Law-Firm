import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
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
from .models import Feedback, Notification, Profile, Quote, Message, Call, Client, ActivityLog
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from advocates.forms import ArticleForm, ContactMessageForm, QuoteForm, ScheduledCallForm
from django.db.models import Count
from django.db.models.functions import TruncDate
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

@login_required
@user_passes_test(admin_required)
def analytics_dashboard(request):
    now = timezone.now()
    start_date = (now - timedelta(days=13)).date()

    # Totals and status breakdowns
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    red_flag_messages = ContactMessage.objects.filter(is_red_flag=True).count()

    total_calls = ScheduledCall.objects.count()
    confirmed_calls = ScheduledCall.objects.filter(is_confirmed=True).count()
    pending_calls = ScheduledCall.objects.filter(is_confirmed=False).count()
    red_flag_calls = ScheduledCall.objects.filter(is_red_flag=True).count()

    total_articles = Article.objects.exclude(type='quote').count()
    total_quotes = Quote.objects.count()
    total_feedbacks = Feedback.objects.count()
    upcoming_events = CalendarEvent.objects.filter(date__gte=now.date()).count()

    # Time-series: last 14 days messages and calls
    msg_qs = (
        ContactMessage.objects.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
    )
    call_qs = (
        ScheduledCall.objects.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
    )

    msg_map = {x['day'].strftime('%Y-%m-%d'): x['count'] for x in msg_qs}
    call_map = {x['day'].strftime('%Y-%m-%d'): x['count'] for x in call_qs}

    labels = []
    msg_series = []
    call_series = []
    for i in range(14):
        d = start_date + timedelta(days=i)
        ds = d.strftime('%Y-%m-%d')
        labels.append(ds)
        msg_series.append(msg_map.get(ds, 0))
        call_series.append(call_map.get(ds, 0))

    context = {
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'red_flag_messages': red_flag_messages,
        'total_calls': total_calls,
        'confirmed_calls': confirmed_calls,
        'pending_calls': pending_calls,
        'red_flag_calls': red_flag_calls,
        'total_articles': total_articles,
        'total_quotes': total_quotes,
        'total_feedbacks': total_feedbacks,
        'upcoming_events': upcoming_events,
        'labels': labels,
        'msg_series': msg_series,
        'call_series': call_series,
    }
    return render(request, 'admin_dashboard/analytics.html', context)


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
    call.is_read = True  # Mark as read before deletion
    call.save()

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

    # Update red flags dynamically
    ContactMessage.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)
    ScheduledCall.objects.filter(is_read=False, created_at__lte=now - timedelta(hours=48)).update(is_red_flag=True)

    # Contact Messages
    for msg in ContactMessage.objects.filter(is_read=False, created_at__isnull=False).order_by("-created_at"):
        notifications.append({
            "id": msg.id,
            "type": "message",
            "subject": msg.subject,
            "client": f"{msg.first_name} {msg.last_name}",
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M"),
            "red_flag": msg.is_red_flag
        })

    # Scheduled Calls
    for call in ScheduledCall.objects.filter(is_read=False, created_at__isnull=False).order_by("-created_at"):
        notifications.append({
            "id": call.id,
            "type": "call",
            "client": f"{call.first_name} {call.last_name}",
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
            return JsonResponse({
                "success": True,
                "message": f"Article '{article.title}' published successfully!",
                "redirect_url": reverse("manage_blogs")
            })
        else:
            errors = {field: [str(e) for e in field_errors] for field, field_errors in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors}, status=400)

    form = ArticleForm()
    categories = Category.objects.all().values_list("id", "name")
    context = {
        "form": form,
        "categories": categories,
    }
    return render(request, "admin_dashboard/article_create.html", context)

   
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
    # Ensure the user has a Profile instance
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Handle profile picture upload
        if 'avatar' in request.FILES:
            profile.image = request.FILES['avatar']
            profile.save()
            messages.success(request, 'Profile picture updated successfully.')
            return redirect('admin_profile')

        # Handle profile information update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        # Skip email update since the template disables it
        # user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully.')

        # Handle password change
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
        elif request.POST.get('old_password'):
            messages.error(request, 'Password change failed. Please check the old password.')

        return redirect('admin_profile')

    # Render the template with the password form
    password_form = PasswordChangeForm(user=request.user)
    context = {
        'password_form': password_form,
    }
    return render(request, 'admin_dashboard/admin_profile.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def admin_required(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(admin_required)
def scheduled_calls_admin(request):
    # Get status filter from query parameters
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    calls = ScheduledCall.objects.order_by('-date', '-time_slot')
    
    # Apply status filter if provided
    if status_filter == 'confirmed':
        calls = calls.filter(is_confirmed=True)
    elif status_filter == 'pending':
        calls = calls.filter(is_confirmed=False)
    
    # Paginate the filtered queryset
    paginator = Paginator(calls, 10)  # Show 10 calls per page
    page_number = request.GET.get('page', 1)  # Default to page 1
    page_obj = paginator.get_page(page_number)
    
    return render(request, "admin_dashboard/scheduled_calls.html", {
        "calls": page_obj,
        "selected_status": status_filter,  # For dropdown persistence
    })


@login_required
@user_passes_test(admin_required)
def activity_log_list(request):
    activities = ActivityLog.objects.order_by('-created_at')
    return render(request, "admin_dashboard/activity_log_list.html", {"activities": activities})

@login_required
@user_passes_test(admin_required)
def red_flag_messages(request):
    cutoff_time = timezone.now() - timedelta(hours=48)

    # Find scheduled calls older than 48h that are still unconfirmed
    overdue_calls = ScheduledCall.objects.filter(
        is_confirmed=False,
        created_at__lte=cutoff_time
    )

    # Automatically mark them as red flags and calculate how long they’ve been pending
    for call in overdue_calls:
        if not call.is_red_flag:
            call.is_red_flag = True
            call.save()

        delta = timezone.now() - call.created_at
        days = delta.days
        hours = delta.seconds // 3600
        call.pending_duration = (
            f"{days} days, {hours} hours" if days or hours else "Less than an hour"
        )

    # Fetch all flagged scheduled calls
    calls = ScheduledCall.objects.filter(is_red_flag=True).order_by('-created_at')

    # Compute pending duration for all displayed calls
    for call in calls:
        delta = timezone.now() - call.created_at
        days = delta.days
        hours = delta.seconds // 3600
        call.pending_duration = (
            f"{days} days, {hours} hours" if days or hours else "Less than an hour"
        )

    return render(
        request,
        "admin_dashboard/red_flag_messages.html",
        {"calls": calls}
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
def dashboard_home(request):
    print(">>> ADMIN DASHBOARD VIEW IS RUNNING <<<")

    # --- Basic dashboard stats ---
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    pending_calls = ScheduledCall.objects.filter(is_confirmed=False).count()
    total_clients = Client.objects.count()
    active_cases = ScheduledCall.objects.filter(is_confirmed=False).count()  # Or another criteria

    # --- Scheduled Calls Over 48h (Pending Only) ---
    cutoff_time = timezone.localtime(timezone.now()) - timedelta(hours=48)
    overdue_scheduled_calls_count = ScheduledCall.objects.filter(
        is_confirmed=False,
        created_at__lte=cutoff_time
    ).count()

    print("DEBUG >>> overdue_scheduled_calls_count =", overdue_scheduled_calls_count)

    # --- Recent activity ---
    recent_activity = ActivityLog.objects.order_by('-created_at')[:10]

    # --- Render template ---
    return render(request, "admin_dashboard/dashboard.html", {
        "unread_messages": unread_messages,
        "pending_calls": pending_calls,
        "total_clients": total_clients,
        "active_cases": active_cases,
        "overdue_scheduled_calls_count": overdue_scheduled_calls_count,
        "recent_activity": recent_activity,
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

    logger = logging.getLogger(__name__)
    logger.info(f"Retrieved feedbacks: {feedbacks.count()} for type={selected_type}")
    return render(request, 'admin_dashboard/feedback_admin.html', {
        'feedbacks': feedbacks,
        'selected_type': selected_type,
    })

def manage_blogs(request):
    selected_type = request.GET.get('type', 'all')
    blogs = Article.objects.exclude(type='quote')  # Exclude 'quote' type
    if selected_type != 'all':
        blogs = blogs.filter(type=selected_type)
    context = {
        'blogs': blogs,
        'selected_type': selected_type,
    }
    return render(request, 'admin_dashboard/manage_blogs.html', context)

def manage_quotes(request):
    selected_sort = request.GET.get('sort', 'all')
    quotes = Quote.objects.all()
    if selected_sort == 'author':
        quotes = quotes.order_by('author')
    context = {
        'quotes': quotes,
        'selected_sort': selected_sort,
    }
    return render(request, 'admin_dashboard/manage_quotes.html', context)

def quote_create(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quote created successfully.')
            return redirect('manage_quotes')
    else:
        form = QuoteForm()
    return render(request, 'admin_dashboard/quote_create.html', {'form': form})

def edit_quote(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quote updated successfully.')
            return redirect('manage_quotes')
    else:
        form = QuoteForm(instance=quote)
    return render(request, 'admin_dashboard/quote_create.html', {'form': form})

@require_POST
def delete_quote(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    quote.delete()
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(admin_required)
def get_events(request):
    """
    Fetch CalendarEvent objects for FullCalendar.
    Returns events in the format expected by FullCalendar.
    """
    try:
        events = CalendarEvent.objects.filter(
            date__gte=timezone.now().date(),
            date__isnull=False
        ).order_by('date', 'time_slot')
        
        event_list = [
            {
                'id': event.id,
                'title': event.title,
                'start': event.date.strftime('%Y-%m-%d'),
                'client': event.client,
                'case_name': event.case_name,
                'event_type': event.event_type,
                'time_slot': event.time_slot.strftime('%H:%M') if event.time_slot else None,
                'color': event.color if event.color else None
            } for event in events
        ]
        return JsonResponse(event_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@login_required
@user_passes_test(admin_required)
def add_event(request):
    """
    Add a new CalendarEvent via AJAX from the calendar modal.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            client = data.get('client')
            case_name = data.get('case_name')
            date = data.get('date')
            event_type = data.get('event_type')
            time_slot = data.get('time_slot')  # Optional, can be null

            if not all([title, client, case_name, date, event_type]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            event = CalendarEvent.objects.create(
                title=title,
                client=client,
                case_name=case_name,
                date=date,
                time_slot=time_slot,
                event_type=event_type,
                created_by=request.user,
                color='#1E90FF' if event_type == 'call' else '#228B22' if event_type == 'meeting' else None
            )

            # Log activity
            ActivityLog.objects.create(
                admin_user=request.user,
                action=f"Added {event_type} event: {title} for {client} ({case_name}) on {date}"
            )

            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.date.strftime('%Y-%m-%d'),
                'client': event.client,
                'case_name': event.case_name,
                'event_type': event.event_type,
                'time_slot': event.time_slot.strftime('%H:%M') if event.time_slot else None,
                'color': event.color
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
@user_passes_test(admin_required)
def edit_event(request, event_id):
    """
    Edit an existing CalendarEvent via AJAX.
    """
    if request.method == 'POST':
        try:
            event = get_object_or_404(CalendarEvent, id=event_id)
            data = json.loads(request.body)
            title = data.get('title')

            if not title:
                return JsonResponse({'error': 'Title is required'}, status=400)

            event.title = title
            event.save()

            # Log activity
            ActivityLog.objects.create(
                admin_user=request.user,
                action=f"Edited event: {title} (ID: {event_id})"
            )

            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.date.strftime('%Y-%m-%d'),
                'client': event.client,
                'case_name': event.case_name,
                'event_type': event.event_type,
                'time_slot': event.time_slot.strftime('%H:%M') if event.time_slot else None,
                'color': event.color
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
@user_passes_test(admin_required)
def delete_event(request, event_id):
    """
    Delete a CalendarEvent via AJAX.
    """
    if request.method == 'POST':
        try:
            event = get_object_or_404(CalendarEvent, id=event_id)
            title = event.title
            event.delete()

            # Log activity
            ActivityLog.objects.create(
                admin_user=request.user,
                action=f"Deleted event: {title} (ID: {event_id})"
            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_POST
@csrf_exempt  # Note: Consider removing csrf_exempt in production
def mark_call_read(request, call_id):
    try:
        call = ScheduledCall.objects.get(id=call_id)
        call.is_read = True
        call.save()
        return JsonResponse({'status': 'success'})
    except ScheduledCall.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Call not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
