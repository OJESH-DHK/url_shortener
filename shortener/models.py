from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string
import random


class ShortenedURL(models.Model):
    """
    Model to store shortened URLs with analytics and user ownership
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urls')
    original_url = models.URLField(max_length=2048, help_text="The original long URL")
    short_code = models.CharField(max_length=30, unique=True, db_index=True, help_text="Unique short code for the URL")
    custom_code = models.BooleanField(default=False, help_text="Whether this is a custom short code")
    
    # Analytics
    click_count = models.PositiveIntegerField(default=0, help_text="Number of times this URL has been accessed")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this short URL expires (optional)")
    
    # Additional features
    is_active = models.BooleanField(default=True, help_text="Whether this URL is active")
    description = models.CharField(max_length=255, blank=True, help_text="Optional description for this URL")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Shortened URL"
        verbose_name_plural = "Shortened URLs"
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}"
    
    def is_expired(self):
        """Check if the URL has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def increment_click_count(self):
        """Increment the click count atomically"""
        self.click_count = models.F('click_count') + 1
        self.save(update_fields=['click_count'])
        self.refresh_from_db()

    def get_short_url(self):
        """Get the full shortened URL"""
        # Change this to your actual hosted URL once you deploy!
        domain = "https://your-domain.com" 
        return f"{domain}/{self.short_code}"


class URLClick(models.Model):
    """
    Model to track individual clicks on shortened URLs for detailed analytics
    """
    url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    referer = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['-clicked_at']
        verbose_name = "URL Click"
        verbose_name_plural = "URL Clicks"
        indexes = [
            models.Index(fields=['url', '-clicked_at']),
        ]
    
    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"