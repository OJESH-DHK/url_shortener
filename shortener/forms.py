from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ShortenedURL
from .utils import is_valid_custom_code, format_url
from django.utils import timezone


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserLoginForm(AuthenticationForm):
    """Form for user login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class URLShortenerForm(forms.ModelForm):
    """Form for creating/editing shortened URLs"""
    custom_code = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Custom short code (optional)'
        }),
        help_text='Leave blank for auto-generated code. Min 3 characters.'
    )
    
    expires_in_days = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Days until expiration (optional)'
        }),
        help_text='Leave blank for no expiration'
    )

    class Meta:
        model = ShortenedURL
        fields = ['original_url', 'description']
        widgets = {
            'original_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your long URL here'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional description'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_original_url(self):
        url = self.cleaned_data.get('original_url')
        if url:
            url = format_url(url)
        return url
    
    def clean_custom_code(self):
        custom_code = self.cleaned_data.get('custom_code', '').strip()
        
        if not custom_code:
            return ''
        
        # Validate custom code format
        is_valid, error_message = is_valid_custom_code(custom_code)
        if not is_valid:
            raise forms.ValidationError(error_message)
        
        # Check if custom code already exists (excluding current instance if editing)
        existing = ShortenedURL.objects.filter(short_code=custom_code)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError("This short code is already taken. Please choose another.")
        
        return custom_code
    
    def clean_expires_in_days(self):
        days = self.cleaned_data.get('expires_in_days')
        if days:
            if days < 1:
                raise forms.ValidationError("Expiration must be at least 1 day.")
            if days > 365:
                raise forms.ValidationError("Expiration cannot exceed 365 days.")
        return days


class URLEditForm(forms.ModelForm):
    """Form for editing existing URLs"""
    expires_in_days = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Days until expiration (optional)'
        }),
        help_text='Leave blank to keep current expiration or remove expiration'
    )

    class Meta:
        model = ShortenedURL
        fields = ['description', 'is_active']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate expires_in_days if there's an expiration date
        if self.instance and self.instance.expires_at:
            days_until_expiry = (self.instance.expires_at - timezone.now()).days
            if days_until_expiry > 0:
                self.initial['expires_in_days'] = days_until_expiry