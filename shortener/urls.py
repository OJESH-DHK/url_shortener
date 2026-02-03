from django.urls import path
from . import views

app_name = 'shortener'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard and URL management
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_url, name='create_url'),
    path('url/<str:short_code>/', views.url_detail, name='url_detail'),
    path('url/<str:short_code>/edit/', views.edit_url, name='edit_url'),
    path('url/<str:short_code>/delete/', views.delete_url, name='delete_url'),
    path('url/<str:short_code>/analytics/', views.analytics, name='analytics'),
    path('url/<str:short_code>/qr/', views.generate_qr_code, name='qr_code'),
    
    # Short URL redirect (should be last to avoid conflicts)
    path('<str:short_code>/', views.redirect_short_url, name='redirect'),
]