"""
Views for customer registration, authentication, and cookie consent.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomerRegistrationForm, CustomerLoginForm
from .models import CookieConsent
import json


def register_view(request):
    """
    Handle customer registration.
    Creates User, Customer, and CustomerProfile records.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('customer_profile')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in automatically after registration
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Banetón.")
            return redirect('customer_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Register - Banetón'
    }
    return render(request, 'customers/register.html', context)


def login_view(request):
    """
    Handle customer login.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('customer_profile')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                
                # Redirect to 'next' parameter if provided, otherwise to profile
                next_url = request.GET.get('next', 'customer_profile')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomerLoginForm()
    
    context = {
        'form': form,
        'title': 'Login - Banetón'
    }
    return render(request, 'customers/login.html', context)


@login_required
def logout_view(request):
    """
    Handle customer logout.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('/')


@login_required
def profile_view(request):
    """
    Display customer profile and purchase history.
    """
    try:
        customer_profile = request.user.customer_profile
        customer = customer_profile.customer
        
        # Get customer's orders
        orders = customer.order_set.all().order_by('-date')[:10]  # Last 10 orders
        
        context = {
            'customer': customer,
            'customer_profile': customer_profile,
            'orders': orders,
            'title': 'My Profile - Banetón'
        }
        return render(request, 'customers/profile.html', context)
    except Exception as e:
        messages.error(request, "Error loading profile. Please contact support.")
        return redirect('/')


@csrf_exempt  # Allow cookies to be set without CSRF for anonymous users
@require_POST
def accept_cookies(request):
    """
    AJAX endpoint to accept cookies.
    Stores consent in database and sets a cookie.
    """
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        
        accepted = data.get('accepted', False)
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create or update consent record
        consent = None
        
        if request.user.is_authenticated:
            # For registered users
            try:
                customer = request.user.customer_profile.customer
                consent, created = CookieConsent.objects.update_or_create(
                    customer=customer,
                    defaults={
                        'accepted': accepted,
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    }
                )
            except Exception as e:
                # User doesn't have customer profile yet, use session
                if not request.session.session_key:
                    request.session.create()
                
                consent, created = CookieConsent.objects.update_or_create(
                    session_key=request.session.session_key,
                    defaults={
                        'accepted': accepted,
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    }
                )
        else:
            # For anonymous users, use session
            if not request.session.session_key:
                request.session.create()
            
            consent, created = CookieConsent.objects.update_or_create(
                session_key=request.session.session_key,
                defaults={
                    'accepted': accepted,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            )
        
        response = JsonResponse({
            'status': 'success',
            'message': 'Cookie preference saved',
            'accepted': accepted
        })
        
        # Set a cookie to remember the choice (1 year)
        response.set_cookie(
            'cookies_accepted',
            'true' if accepted else 'false',
            max_age=365*24*60*60,  # 1 year in seconds
            httponly=False,  # Allow JavaScript to read it
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        import traceback
        print(f"Error in accept_cookies: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)


def check_cookies(request):
    """
    Check if user has already accepted/rejected cookies.
    Used by frontend to show/hide banner.
    """
    # Check cookie first
    cookies_accepted = request.COOKIES.get('cookies_accepted')
    if cookies_accepted:
        return JsonResponse({
            'status': 'exists',
            'accepted': cookies_accepted == 'true'
        })
    
    # Check database
    if request.user.is_authenticated:
        try:
            customer = request.user.customer_profile.customer
            consent = CookieConsent.objects.filter(customer=customer).first()
            if consent:
                return JsonResponse({
                    'status': 'exists',
                    'accepted': consent.accepted
                })
        except:
            pass
    else:
        # Check by session
        session_key = request.session.session_key
        if session_key:
            consent = CookieConsent.objects.filter(session_key=session_key).first()
            if consent:
                return JsonResponse({
                    'status': 'exists',
                    'accepted': consent.accepted
                })
    
    return JsonResponse({
        'status': 'not_exists'
    })
