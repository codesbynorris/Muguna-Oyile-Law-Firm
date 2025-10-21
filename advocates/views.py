from django.forms import ValidationError
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
from .forms import ArticleForm
from .models import Category, Feedback, Quote, TeamMember
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
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
    LEGAL_SERVICES,
    slugify
)


# ---------------------------
# Helpers
# ---------------------------
def send_html_email(subject, template, context, to_email):
    """
    Send a professional HTML email using Django templates.
    Includes print logs for debugging.
    """
    try:
        print("📧 Preparing to send email...")
        print(f"Subject: {subject}")
        print(f"Recipient: {to_email}")
        print(f"Template: {template}")

        # Render the HTML content from the template and context
        html_content = render_to_string(template, context)

        # Create the email message
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.content_subtype = "html"  # Set content type to HTML

        # Send the email
        sent = email.send(fail_silently=False)

        print(f"✅ Email successfully sent: {sent}")
        return sent

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return None
    except Exception as e:
        print("❌ Email sending error:", str(e))
        return None
        
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

def test(request):
    return render(request, "countrycode.html")


def team(request):
    members = TeamMember.objects.all()
    return render(request, 'team.html', {'members': members})


def privacy_policy(request):
    return render(request, "T&C/privacypolicy.html")


def terms_of_service(request):
    return render(request, "T&C/termsofservice.html")

def feedback(request):
    return render(request, "feedback/FAQs.html")

def cookie_policy(request):
    return render(request, 'T&C/cookie_policy.html')
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

def team_list(request):
    members = TeamMember.objects.all()  # Query all members from DB
    return render(request, 'team.html', {'members': members})



# ---------------------------
# Articles
# ---------------------------


def article_list(request, category_slug=None):
    filter_type = request.GET.get('filter', 'publication')
    if filter_type not in ['publication', 'article', 'news']:
        filter_type = 'publication'
    
    categories = Category.objects.all()
    articles = Article.objects.all()
    category = None
    active_category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)
        active_category = category
    else:
        articles = articles.filter(type=filter_type) if filter_type else articles

    quotes = Quote.objects.all()

    context = {
        "articles": articles,
        "categories": categories,
        "active_category": active_category,
        "quotes": quotes,
        "filter_type": filter_type if not category_slug else None,
    }
    return render(request, "articles/articles_insights.html", context)

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    categories = Category.objects.all()
    quotes = Quote.objects.all()
    context = {
        "article": article,
        "categories": categories,
        "quotes": quotes,
    }
    return render(request, "articles/article_detail.html", context)

def write_blog(request):
    categories = [(c.id, c.name) for c in Category.objects.all()]
    type_choices = Article.TYPE_CHOICES  # For the type dropdown

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")
        author = request.POST.get("author")
        type = request.POST.get("type")

        category = Category.objects.get(id=category_id)

        article = Article.objects.create(
            title=title,
            content=content,
            category=category,
            image=image,
            author=author,
            type=type,
            slug=slugify(title),
        )

        return redirect("articles:article_detail", slug=article.slug)

    return render(request, "articles/write_blog.html", {
        "categories": categories,
        "type_choices": type_choices,
    })
# ---------------------------
# Contact & Schedule Call
# ---------------------------
def contact(request):
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
                contact = contact_form.save(commit=False)
                contact.is_read = False
                contact.is_red_flag = False
                contact.save()

                # Auto red flag if older than 48h
                if contact.created_at <= timezone.now() - timedelta(hours=48):
                    contact.is_red_flag = True
                    contact.save()

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
                return redirect("contact")

        # ---------------------------
        # Schedule Call Form
        # ---------------------------
        elif form_type == "schedule":
            call_form = ScheduledCallForm(request.POST)
            if call_form.is_valid():
                date = call_form.cleaned_data["date"]
                time_slot = call_form.cleaned_data["time_slot"]

                # Prevent double booking
                if ScheduledCall.objects.filter(date=date, time_slot=time_slot).exists():
                    messages.error(request, "This slot is already booked. Please choose another.")
                    return redirect("contact")

                call = call_form.save(commit=False)
                call.is_read = False
                call.is_red_flag = False
                call.is_confirmed = False
                call.save()

                # Auto red flag if older than 48h
                if call.created_at <= timezone.now() - timedelta(hours=48):
                    call.is_red_flag = True
                    call.save()

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
                return redirect("contact")

    return render(
        request,
        "contact.html",
        {"contact_form": contact_form, "call_form": call_form, "legal_services": LEGAL_SERVICES},
    )

def contact_us(request):
    contact_form = ContactMessageForm()
    call_form = ScheduledCallForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # ----------- Handle Contact Message -----------
        if form_type == "message":
            print("🚀 contact_us() triggered")
            contact_form = ContactMessageForm(request.POST)

            if contact_form.is_valid():
                contact = contact_form.save()
                print("✅ Contact form validated successfully")

                # Check if older than 48 hours → mark red flag
                if contact.created_at <= timezone.now() - timedelta(hours=48):
                    contact.is_red_flag = True
                    contact.save()

                # Send admin email
                print("📨 Sending admin email to:", settings.CONTACT_RECEIVER_EMAIL)
                send_html_email(
                    subject=f"📩 New Contact Message - {contact.subject}",
                    template="emails/contact_admin.html",
                    context={"contact": contact, "firm_name": "Law Firm"},
                    to_email=settings.CONTACT_RECEIVER_EMAIL,
                )

                # Send user email
                print("📨 Sending confirmation email to:", contact.email)
                send_html_email(
                    subject="✅ We received your message",
                    template="emails/contact_user.html",
                    context={"contact": contact, "firm_name": "Law Firm"},
                    to_email=contact.email,
                )

                return redirect("/contact/?sent=1")
            else:
                print("❌ Contact form validation errors:", contact_form.errors)

        # ----------- Handle Scheduled Call -----------
        elif form_type == "schedule":
            call_form = ScheduledCallForm(request.POST)

            if call_form.is_valid():
                date = call_form.cleaned_data["date"]
                time_slot = call_form.cleaned_data["time_slot"]

                if ScheduledCall.objects.filter(date=date, time_slot=time_slot).exists():
                    print("⚠️ Slot already taken:", date, time_slot)
                    return redirect("/contact/?sent=slot_taken")

                call = call_form.save()


                # Mark as red flag if older than 48h
                if call.created_at <= timezone.now() - timedelta(hours=48):
                    call.is_red_flag = True
                    call.save()

                # Send admin email
                print("📨 Sending admin email for scheduled call")
                send_html_email(
                    subject=f"📅 New Call Request - {call.first_name} {call.last_name}",
                    template="emails/call_admin.html",
                    context={"call": call, "firm_name": "Law Firm"},
                    to_email=settings.CONTACT_RECEIVER_EMAIL,
                )

                # Send user email
                print("📨 Sending confirmation email to:", call.email)
                send_html_email(
                    subject="⏳ Call Request Received",
                    template="emails/call_user.html",
                    context={"call": call, "firm_name": "Law Firm"},
                    to_email=call.email,
                )

                return redirect("/contact/?sent=1")

            else:
                print("❌ Scheduled Call form validation errors:", call_form.errors)

    # Default: GET or invalid POST
    return render(
        request,
        "contact.html",
        {
            "contact_form": contact_form,
            "call_form": call_form,
            "legal_services": LEGAL_SERVICES,
        },
    )# Admin Dashboard
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
@user_passes_test(lambda u: u.is_staff)
def confirm_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)

    # Update call status
    call.is_confirmed = True
    call.is_read = True

    # Red flag check (older than 48h)
    if call.created_at <= timezone.now() - timedelta(hours=48):
        call.is_red_flag = True

    call.save()

    # Create CalendarEvent if not exists
    if not call.calendar_event:
        event_title = f"Call with {call.first_name} {call.last_name} at {call.time_slot.strftime('%H:%M')}"
        event = CalendarEvent.objects.create(
            title=event_title,
            client=f"{call.first_name} {call.last_name}",
            case_name=getattr(call, 'subject', ''),
            date=call.date,
            time_slot=call.time_slot,
            event_type=CalendarEvent.CALL,
            created_by=request.user
        )
        call.calendar_event = event
        call.save()

    # Log admin activity
    ActivityLog.objects.create(
        admin_user=request.user,
        action=f"Confirmed call: {call.first_name} {call.last_name} at {call.time_slot.strftime('%H:%M')}"
    )

    # Send confirmation email
    current_site = get_current_site(request)
    site_url = f"http://{current_site.domain}"
    send_html_email(
        subject="✅ Your call has been confirmed",
        template="emails/call_confirmed.html",
        context={
            "call": call,
            "firm_name": "Muguna Oyile Law Firm",
            "site_url": site_url,
            "booking_link": f"{site_url}/contact",
        },
        to_email=call.email,
    )

    messages.success(request, f"Call with {call.first_name} confirmed and added to calendar.")
    return redirect("admin_dashboard")

@login_required
@user_passes_test(admin_check)
def decline_call(request, call_id):
    call = get_object_or_404(ScheduledCall, id=call_id)

    # Update call status
    call.is_confirmed = False
    call.is_read = True

    # Red flag check
    if call.created_at <= timezone.now() - timedelta(hours=48):
        call.is_red_flag = True

    call.save()

    # Log admin activity
    ActivityLog.objects.create(
        admin_user=request.user,
        action=f"Declined call: {call.first_name} {call.last_name} for {getattr(call, 'subject', '')}"
    )

    # Send decline email
    current_site = get_current_site(request)
    site_url = f"http://{current_site.domain}"
    send_html_email(
        subject="❌ Your call request was declined",
        template="emails/call_declined.html",
        context={
            "call": call,
            "firm_name": "Muguna Oyile Law Firm",
            "site_url": site_url,
            "booking_link": f"{site_url}/contact",
        },
        to_email=call.email,
    )

    messages.success(request, f"Call with {call.first_name} declined. User notified.")
    return redirect("admin_dashboard")


@login_required
@user_passes_test(lambda u: u.is_staff)
def all_notifications(request):
    # Fetch all items
    messages_list = ContactMessage.objects.all().order_by("-created_at")
    calls_list = ScheduledCall.objects.all().order_by("-created_at")
    red_flags = AdminActivityLog.objects.all().order_by("-created_at")

    # Convert each queryset into a common dict structure
    notifications = []

    for m in messages_list:
        notifications.append({
            "type": "message",
            "client": f"{m.first_name} {m.last_name}",
            "subject": m.subject,
            "created_at": m.created_at,
            "red_flag": m.is_red_flag
        })

    for c in calls_list:
        notifications.append({
            "type": "call",
            "client": f"{c.first_name} {c.last_name}",
            "subject": getattr(c, "subject", "N/A"),
            "created_at": c.created_at,
            "red_flag": c.is_red_flag
        })

    for r in red_flags:
        notifications.append({
            "type": "activity",
            "client": getattr(r, "user", "Admin"),
            "subject": getattr(r, "action", "N/A"),
            "created_at": r.created_at,
            "red_flag": True
        })

    # Sort combined list by created_at descending
    notifications.sort(key=lambda x: x["created_at"], reverse=True)

    context = {
        "notifications": notifications,
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

def admin_required(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(admin_required)
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)

        form.fields['category'].queryset = Category.objects.all()

        if form.is_valid():
            article = form.save()
            return JsonResponse({"success": True, "message": "✅ Blog published successfully!"})
        else:
            errors = {field: error.get_json_data() for field, error in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors})
    else:
        form = ArticleForm()
    return render(request, "admin_dashboard/article_create.html", {"form": form})

def schedule_call(request):
    if request.method == "POST":
        ScheduledCall.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone_number=request.POST.get('phone'),
            subject=request.POST.get('subject'),
            date=request.POST.get('date'),
            time_slot=request.POST.get('time_slot')
        )
        messages.success(request, "Your call request has been submitted successfully!")
        return redirect('contact')
    return render(request, "schedule_call.html")

def feedback_page(request):
    if request.method == "POST":
        print("✅ Received POST request")
        print("Form data:", request.POST)
        feedback_type = request.POST.get("feedback-type")
        name = request.POST.get("name")
        email = request.POST.get("email")
        comments = request.POST.get("comments")
        rating = request.POST.get("rating")
        print(f"Feedback: type={feedback_type}, name={name}, email={email}, comments={comments}, rating={rating}")

        try:
            feedback = Feedback.objects.create(
                name=name,
                email=email,
                feedback_type=feedback_type,
                comments=comments,
                rating=int(rating) if rating else 0,
            )
            print(f"Feedback saved successfully: {feedback}")
            return JsonResponse({"success": True})
        except ValidationError as e:
            print(f"Validation error: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return JsonResponse({"success": False, "error": "An error occurred while saving feedback."}, status=500)

    return render(request, "feedback/FAQs.html")