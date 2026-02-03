from django.contrib import admin
from .models import ShortenedURL, URLClick


@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'original_url_truncated', 'user', 'click_count', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'custom_code', 'created_at', 'expires_at']
    search_fields = ['short_code', 'original_url', 'user__username', 'description']
    readonly_fields = ['click_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('URL Information', {
            'fields': ('user', 'original_url', 'short_code', 'custom_code', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Analytics', {
            'fields': ('click_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def original_url_truncated(self, obj):
        """Display truncated original URL"""
        max_length = 50
        if len(obj.original_url) > max_length:
            return obj.original_url[:max_length] + '...'
        return obj.original_url
    original_url_truncated.short_description = 'Original URL'


@admin.register(URLClick)
class URLClickAdmin(admin.ModelAdmin):
    list_display = ['url', 'clicked_at', 'ip_address', 'user_agent_truncated']
    list_filter = ['clicked_at']
    search_fields = ['url__short_code', 'ip_address']
    readonly_fields = ['url', 'clicked_at', 'ip_address', 'user_agent', 'referer']
    date_hierarchy = 'clicked_at'
    
    def user_agent_truncated(self, obj):
        """Display truncated user agent"""
        max_length = 50
        if len(obj.user_agent) > max_length:
            return obj.user_agent[:max_length] + '...'
        return obj.user_agent
    user_agent_truncated.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        """Disable manual click creation"""
        return False