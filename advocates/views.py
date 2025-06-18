from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage


def index(request):
    """
    Main view that handles both GET and POST requests for the contact form.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Here you would typically:
            # 1. Save to database (if you have a model)
            # 2. Send email (using send_mail or EmailMessage)
            # 3. Integrate with a CRM or ticket system
            
            # Example debug output (remove in production)
            print(f"New contact: {name} ({email})\nMessage: {message}")
            
            # Success message
            messages.success(request, 'Thank you for your message! We will contact you soon.')
            
            # Redirect to prevent form resubmission
            return redirect(reverse('home'))  # Make sure 'home' is defined in your urls.py
            
    else:
        form = ContactForm()
    
    return render(request, 'advocates/index.html', {
        'form': form,
        # Add any additional context variables here
    })

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')
            message = form.cleaned_data['message']
            
            # Prepare email content
            email_message = f"""
            New contact form submission:
            
            Name: {name}
            Email: {email}
            Phone: {phone if phone else 'Not provided'}
            
            Message:
            {message}
            """
            
            try:
                send_mail(
                    subject=f"New Contact Message from {name}",
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,  # From your settings
                    recipient_list=[settings.CONTACT_EMAIL],  # Your law firm's email
                    fail_silently=False,
                )
                messages.success(request, "Thank you for your message! We'll contact you soon.")
                return redirect('contact')  # Redirect to prevent form resubmission
            except Exception as e:
                messages.error(request, "There was an error sending your message. Please try again later.")
                # Log the error if needed
                print(f"Email sending failed: {str(e)}")
    else:
        form = ContactForm()
    
    return render(request, 'advocates/contact.html', {'form': form})

def index(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message_text = form.cleaned_data['message']

            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message_text
            )

            # Send auto-reply
            send_mail(
                subject='Thank You for Contacting Muguna & Oyugi',
                message=f"Dear {name},\n\nThank you for reaching out. We’ve received your message and will respond shortly.\n\nBest regards,\nMuguna & Oyugi Team",
                from_email='noreply@yourdomain.com',
                recipient_list=[email],
                fail_silently=False
            )

            # Optional: Notify admin (you)
            send_mail(
                subject=f'New Contact Message from {name}',
                message=message_text,
                from_email=email,
                recipient_list=['norrishenry309@gmail.com'],
                fail_silently=True
            )

            messages.success(request, "Your message has been sent successfully.")
            return redirect('home')
    else:
        form = ContactForm()

    return render(request, 'advocates/index.html', {'form': form})