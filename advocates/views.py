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
from .models import ContactSubmission

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
    services = [
        {
            'slug': 'tax',
            'icon': 'fas fa-file-invoice-dollar',
            'title': 'Tax Advisory',
            'summary': 'Comprehensive tax consultancy and representation services to ensure compliance and optimize your tax position.',
            'details': [
                'Tax planning and compliance advisory',
                'Representation before tax authorities',
                'Tax dispute resolution',
                'Transfer pricing documentation',
                'Tax due diligence for transactions',
                'Customs and excise duty advisory',
            ],
        },
        {
            'slug': 'data',
            'icon': 'fas fa-database',
            'title': 'Data Protection',
            'summary': 'Guidance on data privacy laws and implementation of robust data protection frameworks.',
            'details': [
                'Data protection compliance audits',
                'Privacy policy drafting',
                'Data processing agreements',
                'Data breach response planning',
                'Employee training programs',
                'Representation before data commissioner',
            ],
        },
        {
            'slug': 'immigration',
            'icon': 'fas fa-passport',
            'title': 'Immigration',
            'summary': 'End-to-end support for work permits, visas, and citizenship matters.',
            'details': [
                'Work permit applications',
                'Dependent pass processing',
                'Citizenship and naturalization',
                'Immigration appeals',
                'Employer compliance advisory',
                'Expatriate tax planning',
            ],
        },
        {
            'slug': 'ip',
            'icon': 'fas fa-copyright',
            'title': 'Intellectual Property',
            'summary': 'Protection and enforcement of intellectual property rights.',
            'details': [
                'Trademark registration',
                'Patent filing and prosecution',
                'Copyright protection',
                'Industrial design registration',
                'IP licensing agreements',
                'Anti-counterfeiting measures',
            ],
        },
    ]
    return render(request, 'Services/consultancy_services.html', {'services': services})


def corporate_commercial(request):
    services = [
        {
            'slug': 'entity',
            'icon': 'fas fa-building',
            'title': 'Entity Formation',
            'summary': 'We provide comprehensive legal support for establishing various business entities, ensuring compliance with all regulatory requirements from inception.',
            'details': [
                'Company incorporation (private and public limited)',
                'Registration of public benefit organizations',
                'Cooperative society formation',
                'Trust and foundation establishment',
                'Ongoing secretarial services and compliance',
                'Corporate governance structuring',
            ],
        },
        {
            'slug': 'contracts',
            'icon': 'fas fa-handshake',
            'title': 'Commercial Contracts',
            'summary': 'Our team drafts, reviews, and negotiates commercial agreements that protect your interests while facilitating successful business relationships.',
            'details': [
                'Shareholder and partnership agreements',
                'Joint venture documentation',
                'Supply and distribution contracts',
                'Service level agreements',
                'Confidentiality and non-disclosure agreements',
                'Contract dispute resolution',
            ],
        },
        {
            'slug': 'compliance',
            'icon': 'fas fa-search',
            'title': 'Regulatory Compliance',
            'summary': 'We help businesses navigate complex regulatory landscapes with comprehensive compliance solutions tailored to your industry.',
            'details': [
                'Compliance audits and gap analysis',
                'Regulatory risk assessments',
                'Policy and procedure development',
                'Industry-specific compliance training',
                'Licensing and permit applications',
                'Ongoing compliance monitoring',
            ],
        },
        {
            'slug': 'mergers',
            'icon': 'fas fa-random',
            'title': 'Mergers & Acquisitions',
            'summary': 'Our end-to-end M&A services ensure smooth business combinations while mitigating legal and financial risks.',
            'details': [
                'Due diligence investigations',
                'Deal structuring and valuation',
                'Transaction documentation',
                'Competition law compliance',
                'Post-merger integration',
                'Dispute resolution in M&A transactions',
            ],
        },
    ]
    return render(request, 'Services/corporate_commercial.html', {'services': services})


def property_law(request):
    services = [
        {
            'slug': 'conveyancing',
            'icon': 'fas fa-file-contract',
            'title': 'Conveyancing',
            'summary': 'Expert handling of property transfers and title documentation.',
            'details': [
                'Sale and purchase agreements',
                'Title searches and due diligence',
                'Transfer documentation',
                'Stamp duty assessment',
                'Registration with lands registry',
                'Sectional properties transactions',
            ],
        },
        {
            'slug': 'leases',
            'icon': 'fas fa-home',
            'title': 'Leases & Tenancies',
            'summary': 'Comprehensive lease documentation and tenancy management.',
            'details': [
                'Commercial lease preparation',
                'Residential tenancy agreements',
                'Lease registration',
                'Rent review advisory',
                'Forfeiture proceedings',
                'Tenant eviction services',
            ],
        },
        {
            'slug': 'finance',
            'icon': 'fas fa-hand-holding-usd',
            'title': 'Property Finance',
            'summary': 'Legal support for property financing transactions.',
            'details': [
                'Mortgage documentation',
                'Charge and debenture preparation',
                'Loan security perfection',
                'Foreclosure proceedings',
                'Refinancing advisory',
                'Construction financing',
            ],
        },
        {
            'slug': 'disputes',
            'icon': 'fas fa-landmark',
            'title': 'Land Disputes',
            'summary': 'Resolution of complex land and property conflicts.',
            'details': [
                'Boundary disputes',
                'Adverse possession claims',
                'Title rectification',
                'Easement and right of way',
                'Compulsory acquisition',
                'Environmental court matters',
            ],
        },
    ]
    return render(request, 'Services/property_law.html', {'services': services})


def dispute_resolution(request):
    services = [
        {
            'id': 'negotiation',
            'icon': 'fas fa-handshake',
            'title': 'Negotiation',
            'summary': 'We help parties reach fair agreements outside of court through strategic dialogue.',
            'details': [
                'Commercial settlements',
                'Property negotiations',
                'Employment contract resolutions',
                'Business partner agreements',
            ],
        },
        {
            'id': 'mediation',
            'icon': 'fas fa-comments',
            'title': 'Mediation',
            'summary': 'Our mediators guide parties to voluntary resolutions through structured communication.',
            'details': [
                'Family and custody mediation',
                'Land and boundary disputes',
                'Employment grievance handling',
                'Debt settlement mediation',
            ],
        },
        {
            'id': 'arbitration',
            'icon': 'fas fa-gavel',
            'title': 'Arbitration',
            'summary': 'We represent clients in arbitration for fair and binding conflict resolution.',
            'details': [
                'Commercial arbitration',
                'Construction contract disputes',
                'Sports and entertainment arbitration',
                'International arbitration proceedings',
            ],
        },
        {
            'id': 'litigation',
            'icon': 'fas fa-balance-scale',
            'title': 'Litigation Support',
            'summary': 'We handle court disputes with strategy and strong advocacy in all legal forums.',
            'details': [
                'Case strategy development',
                'Legal document drafting',
                'Trial representation',
                'Appeals and judicial reviews',
            ],
        },
    ]
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
