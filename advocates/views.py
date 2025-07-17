import uuid
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactSubmission, ConsultancyService, CorporateService, DisputeService, PropertyService

# ────────────────────────────────
# BASIC PAGE VIEWS
# ────────────────────────────────

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def team(request):
    return render(request, 'team.html')

def contact(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')


# ────────────────────────────────
# SERVICE PAGES
# ────────────────────────────────

def services(request):
    return render(request, 'testing/legal.html')

def consultancy_services(request):
    services = ConsultancyService.objects.filter(published=True).prefetch_related('details')
    return render(request, 'Services/consultancy_services.html', {'services': services})

def corporate_commercial(request):
    services = CorporateService.objects.filter(published=True).prefetch_related('details')
    return render(request, 'Services/corporate_commercial.html', {'services': services})

def property_law(request):
    services = PropertyService.objects.filter(published=True).prefetch_related('details')
    return render(request, 'Services/property_law.html', {'services': services})

def dispute_resolution(request):
    services = DisputeService.objects.filter(published=True).prefetch_related('details')
    return render(request, 'Services/dispute_resolution.html', {'services': services})

# ────────────────────────────────
# NEWSLETTER SUBSCRIPTION
# ────────────────────────────────

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # TODO: Save email to model or 3rd-party tool
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

        # ────── Admin Email ──────
        html_admin = f"""
        <html><body style="font-family: Arial, sans-serif; background: #f9f9f9; color: #0a1a30; padding: 30px;">
          <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 8px; padding: 30px; box-shadow: 0 8px 20px rgba(0,0,0,0.05);">
            <div style="text-align: center;"><img src="{logo_url}" alt="Muguna & Oyile Advocates" style="max-width: 180px; margin-bottom: 20px;"></div>
            <h2>📩 New Contact Submission</h2>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Ticket ID:</strong> {ticket_id}</p>
            <p><strong>Name:</strong> {name}<br><strong>Email:</strong> {email}<br><strong>IP Address:</strong> {ip_address}<br><strong>Time:</strong> {timestamp}</p>
            <hr style="margin: 20px 0;">
            <p><strong>Message:</strong></p>
            <p style="background: #f4f4f4; padding: 10px; border-left: 4px solid #c9a769;">{message}</p>
          </div></body></html>
        """

        send_mail(
            subject=f"[M&O Contact] {subject} (Ticket: {ticket_id})",
            message=strip_tags(html_admin),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            html_message=html_admin,
        )

        # ────── Auto-reply to User ──────
        html_user = f"""
        <html><body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px; color: #0a1a30;">
          <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 8px; padding: 30px; box-shadow: 0 8px 20px rgba(0,0,0,0.05);">
            <div style="text-align: center;"><img src="{logo_url}" alt="Muguna & Oyile Advocates" style="max-width: 180px; margin-bottom: 20px;"></div>
            <h2>Hello {name},</h2>
            <p>Thank you for reaching out to <strong>Muguna & Oyile Advocates</strong>.</p>
            <p>We’ve received your message regarding <em>{subject}</em> and will respond as soon as possible.</p>
            <p style="background: #f2f2f2; padding: 10px; border-left: 4px solid #c9a769;">
              🎫 <strong>Your Ticket ID:</strong> {ticket_id}
            </p>
            <p>If your matter is urgent, don’t hesitate to call or WhatsApp us directly.</p>
            <hr style="margin: 30px 0; border-top: 1px solid #eee;">
            <p><strong>Contact Details:</strong><br>
              📍 24th Floor, Britam Towers, Nairobi<br>
              📞 <a href="tel:+254103758354" style="color:#0a1a30;">+254 103 758 354</a><br>
              ✉️ <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" style="color:#0a1a30;">{settings.DEFAULT_FROM_EMAIL}</a>
            </p>
            <p style="margin-top: 40px;">Warm regards,<br><strong>The Muguna & Oyile Team</strong></p>
          </div></body></html>
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
        print("EMAIL ERROR:", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
