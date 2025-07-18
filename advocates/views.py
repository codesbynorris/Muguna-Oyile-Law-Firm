import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    ContactSubmission,
    ConsultancyService,
    CorporateService,
    DisputeService,
    PropertyService,
)

# ────────────────────────────────
# STATIC PAGES (Cached)
# ────────────────────────────────

@cache_page(60 * 30)
def home(request):
    return render(request, 'home.html')

@cache_page(60 * 60)
def about(request):
    return render(request, 'about.html')

@cache_page(60 * 60)
def team(request):
    return render(request, 'team.html')

@cache_page(60 * 60)
def contact(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'T&C/privacypolicy.html')

def terms_of_service(request):
    return render(request, 'T&C/termsofservice.html')


# ────────────────────────────────
# SERVICES LANDING PAGE
# ────────────────────────────────

@cache_page(60 * 30)
def services(request):
    context = {
        'consultancy_services': ConsultancyService.objects.filter(published=True),
        'corporate_services': CorporateService.objects.filter(published=True),
        'dispute_services': DisputeService.objects.filter(published=True),
        'property_services': PropertyService.objects.filter(published=True),
    }
    return render(request, 'services/services_home.html', context)


# ────────────────────────────────
# SERVICE CATEGORY VIEWS (Cached + prefetch_related + cache.set)
# ────────────────────────────────

@cache_page(60 * 15)
def consultancy_services(request):
    services = cache.get('consultancy_services')
    if not services:
        services = ConsultancyService.objects.filter(published=True).prefetch_related('details')
        cache.set('consultancy_services', services, 60 * 15)
    return render(request, 'services/consultancy_services.html', {'services': services})

@cache_page(60 * 15)
def corporate_commercial(request):
    services = cache.get('corporate_services')
    if not services:
        services = CorporateService.objects.filter(published=True).prefetch_related('details')
        cache.set('corporate_services', services, 60 * 15)
    return render(request, 'services/corporate_commercial.html', {'services': services})

@cache_page(60 * 15)
def dispute_resolution(request):
    services = cache.get('dispute_services')
    if not services:
        services = DisputeService.objects.filter(published=True).prefetch_related('details')
        cache.set('dispute_services', services, 60 * 15)
    return render(request, 'services/dispute_resolution.html', {'services': services})

@cache_page(60 * 15)
def property_law(request):
    services = cache.get('property_services')
    if not services:
        services = PropertyService.objects.filter(published=True).prefetch_related('details')
        cache.set('property_services', services, 60 * 15)
    return render(request, 'services/property_law.html', {'services': services})


# ────────────────────────────────
# SERVICE DETAIL VIEWS
# ────────────────────────────────

@cache_page(60 * 30)
def consultancy_detail(request, slug):
    service = get_object_or_404(ConsultancyService, slug=slug, published=True)
    return render(request, 'services/consultancy_detail.html', {'service': service})

@cache_page(60 * 30)
def corporate_detail(request, slug):
    service = get_object_or_404(CorporateService, slug=slug, published=True)
    return render(request, 'services/corporate_detail.html', {'service': service})

@cache_page(60 * 30)
def dispute_detail(request, slug):
    service = get_object_or_404(DisputeService, slug=slug, published=True)
    return render(request, 'services/dispute_detail.html', {'service': service})

@cache_page(60 * 30)
def property_detail(request, slug):
    service = get_object_or_404(PropertyService, slug=slug, published=True)
    return render(request, 'services/property_detail.html', {'service': service})


# ────────────────────────────────
# NEWSLETTER SUBSCRIPTION
# ────────────────────────────────

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Optional: Save to DB or third-party API
        return render(request, 'subscription_success.html')
    return redirect('home')


# ────────────────────────────────
# CONTACT FORM EMAIL HANDLER
# ────────────────────────────────

@csrf_protect
@require_POST
def send_contact_email(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([name, email, subject, message]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

        ticket_id = f"M&O-{uuid.uuid4().hex[:8].upper()}"
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0]

        ContactSubmission.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            ip_address=ip_address,
            ticket_id=ticket_id,
        )

        timestamp = now().strftime("%A, %d %B %Y at %I:%M %p")
        logo_url = "https://raw.githubusercontent.com/codesbynorris/Muguna-Oyile-Law-Firm/master/advocates/static/images/logo.png"

        # Admin Email
        html_admin = f"""
        <html><body style="font-family: Arial, sans-serif;">
        <div style="max-width:600px;margin:auto;background:#fff;padding:30px;border-radius:8px;">
        <div style="text-align:center;"><img src="{logo_url}" alt="Logo" style="max-width:180px;"></div>
        <h2>📩 New Contact Submission</h2>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Ticket ID:</strong> {ticket_id}</p>
        <p><strong>Name:</strong> {name}<br><strong>Email:</strong> {email}<br><strong>IP:</strong> {ip_address}<br><strong>Time:</strong> {timestamp}</p>
        <hr><p><strong>Message:</strong><br>{message}</p></div></body></html>
        """

        send_mail(
            subject=f"[M&O Contact] {subject} (Ticket: {ticket_id})",
            message=strip_tags(html_admin),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            html_message=html_admin,
        )

        # Auto-reply to user
        html_user = f"""
        <html><body style="font-family: Arial, sans-serif;">
        <div style="max-width:600px;margin:auto;background:#fff;padding:30px;border-radius:8px;">
        <div style="text-align:center;"><img src="{logo_url}" alt="Logo" style="max-width:180px;"></div>
        <h2>Hello {name},</h2>
        <p>Thanks for contacting Muguna & Oyile Advocates.</p>
        <p>Your ticket ID is <strong>{ticket_id}</strong>.</p>
        <p>We’ll respond shortly. For urgent matters, reach out directly.</p>
        <hr><p>📞 <a href="tel:+254103758354">+254 103 758 354</a><br>
        ✉️ <a href="mailto:{settings.DEFAULT_FROM_EMAIL}">{settings.DEFAULT_FROM_EMAIL}</a></p>
        <p>Warm regards,<br><strong>The M&O Team</strong></p></div></body></html>
        """

        send_mail(
            subject="We Received Your Message – Muguna & Oyile Advocates",
            message=strip_tags(html_user),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_user,
        )

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
