from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponse, Http404
from datetime import timedelta
import qrcode
from io import BytesIO

from .models import ShortenedURL, URLClick
from .forms import UserRegistrationForm, UserLoginForm, URLShortenerForm, URLEditForm
from .utils import generate_unique_short_code, get_client_ip


def home(request):
    """Home page view"""
    context = {
        'total_urls': ShortenedURL.objects.count(),
        'total_clicks': ShortenedURL.objects.aggregate(total=Count('clicks'))['total'] or 0,
    }
    return render(request, 'shortener/home.html', context)


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('shortener:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('shortener:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'shortener/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('shortener:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'shortener:dashboard')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'shortener/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('shortener:home')


@login_required
def dashboard(request):
    """Dashboard view showing user's URLs"""
    urls = ShortenedURL.objects.filter(user=request.user).select_related('user').prefetch_related('clicks')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        urls = urls.filter(
            Q(original_url__icontains=search_query) |
            Q(short_code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Sort functionality
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-click_count', 'click_count', 'short_code', '-short_code']
    if sort_by in valid_sorts:
        urls = urls.order_by(sort_by)
    
    # Calculate stats
    stats = {
        'total_urls': urls.count(),
        'total_clicks': sum(url.click_count for url in urls),
        'active_urls': urls.filter(is_active=True).count(),
        'expired_urls': sum(1 for url in urls if url.is_expired()),
    }
    
    context = {
        'urls': urls,
        'stats': stats,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'shortener/dashboard.html', context)


@login_required
def create_url(request):
    """Create a new shortened URL"""
    if request.method == 'POST':
        form = URLShortenerForm(request.POST, user=request.user)
        if form.is_valid():
            shortened_url = form.save(commit=False)
            shortened_url.user = request.user
            
            # Handle custom code or generate one
            custom_code = form.cleaned_data.get('custom_code')
            if custom_code:
                shortened_url.short_code = custom_code
                shortened_url.custom_code = True
            else:
                shortened_url.short_code = generate_unique_short_code(ShortenedURL)
            
            # Handle expiration
            expires_in_days = form.cleaned_data.get('expires_in_days')
            if expires_in_days:
                shortened_url.expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            shortened_url.save()
            messages.success(request, f'Short URL created successfully: {shortened_url.short_code}')
            return redirect('shortener:url_detail', short_code=shortened_url.short_code)
    else:
        form = URLShortenerForm(user=request.user)
    
    return render(request, 'shortener/create_url.html', {'form': form})


@login_required
def url_detail(request, short_code):
    """View details of a specific URL"""
    url = get_object_or_404(ShortenedURL, short_code=short_code, user=request.user)
    
    # Get recent clicks
    recent_clicks = url.clicks.all()[:10]
    
    context = {
        'url': url,
        'recent_clicks': recent_clicks,
        'is_expired': url.is_expired(),
    }
    return render(request, 'shortener/url_detail.html', context)


@login_required
def edit_url(request, short_code):
    """Edit an existing URL"""
    url = get_object_or_404(ShortenedURL, short_code=short_code, user=request.user)
    
    if request.method == 'POST':
        form = URLEditForm(request.POST, instance=url)
        if form.is_valid():
            updated_url = form.save(commit=False)
            
            # Handle expiration update
            expires_in_days = form.cleaned_data.get('expires_in_days')
            if expires_in_days:
                updated_url.expires_at = timezone.now() + timedelta(days=expires_in_days)
            elif expires_in_days == 0:
                updated_url.expires_at = None
            
            updated_url.save()
            messages.success(request, 'URL updated successfully!')
            return redirect('shortener:url_detail', short_code=short_code)
    else:
        form = URLEditForm(instance=url)
    
    context = {
        'form': form,
        'url': url,
    }
    return render(request, 'shortener/edit_url.html', context)


@login_required
def delete_url(request, short_code):
    """Delete a URL"""
    url = get_object_or_404(ShortenedURL, short_code=short_code, user=request.user)
    
    if request.method == 'POST':
        url.delete()
        messages.success(request, 'URL deleted successfully!')
        return redirect('shortener:dashboard')
    
    return render(request, 'shortener/delete_url.html', {'url': url})


def redirect_short_url(request, short_code):
    """Redirect to the original URL and track the click"""
    url = get_object_or_404(ShortenedURL, short_code=short_code)
    
    # Check if URL is active
    if not url.is_active:
        messages.error(request, 'This short URL has been deactivated.')
        return render(request, 'shortener/url_inactive.html', {'url': url})
    
    # Check if URL is expired
    if url.is_expired():
        messages.error(request, 'This short URL has expired.')
        return render(request, 'shortener/url_expired.html', {'url': url})
    
    # Track the click
    URLClick.objects.create(
        url=url,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        referer=request.META.get('HTTP_REFERER')
    )
    
    # Increment click count
    url.increment_click_count()
    
    # Redirect to original URL
    return redirect(url.original_url)


@login_required
def generate_qr_code(request, short_code):
    """Generate QR code for a shortened URL"""
    url = get_object_or_404(ShortenedURL, short_code=short_code, user=request.user)
    
    # Build the full short URL
    short_url = request.build_absolute_uri(f'/{url.short_code}')
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(short_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Return as HTTP response
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'inline; filename=qr_{short_code}.png'
    return response


@login_required
def analytics(request, short_code):
    """View detailed analytics for a URL"""
    url = get_object_or_404(ShortenedURL, short_code=short_code, user=request.user)
    
    # Get clicks with aggregation by date
    clicks_by_date = url.clicks.extra(
        select={'date': 'DATE(clicked_at)'}
    ).values('date').annotate(count=Count('id')).order_by('-date')[:30]
    
    context = {
        'url': url,
        'clicks_by_date': clicks_by_date,
        'total_clicks': url.click_count,
        'recent_clicks': url.clicks.all()[:20],
    }
    return render(request, 'shortener/analytics.html', context)

def handler404(request, exception=None):
    return render(request, 'shortener/404.html', status=404)