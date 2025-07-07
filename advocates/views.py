from django.shortcuts import redirect, render

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'testing/legal.html')

def consultancyservices(request):
    return render(request, 'Services/consultancy.html')

def corporateservices(request):
    return render(request, 'Services/corporate.html')

def disputeresolutionservices(request):
    return render(request, 'Services/dispute_resolution.html')

def propertyservices(request):
    return render(request, 'Services/property.html')


def team(request):
    return render(request, 'team.html')

def contact(request):
    return render(request, 'contact.html')

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here you would typically:
        # 1. Validate the email
        # 2. Save to database
        # 3. Send confirmation email
        return render(request, 'subscription_success.html')
    return redirect('home')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')