import string
import random
import hashlib
from django.utils import timezone


def generate_short_code(length=6):
    """
    Generate a random short code using base62 encoding (alphanumeric)
    
    Args:
        length: Length of the short code (default 6)
    
    Returns:
        A random string of specified length
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def generate_unique_short_code(model_class, length=6, max_attempts=10):
    """
    Generate a unique short code that doesn't exist in the database
    
    Args:
        model_class: The model class to check against (ShortenedURL)
        length: Length of the short code
        max_attempts: Maximum number of attempts to find a unique code
    
    Returns:
        A unique short code string
    
    Raises:
        ValueError: If unable to generate unique code after max_attempts
    """
    for _ in range(max_attempts):
        short_code = generate_short_code(length)
        if not model_class.objects.filter(short_code=short_code).exists():
            return short_code
    
    # If we couldn't find a unique code, try with longer length
    return generate_unique_short_code(model_class, length + 1, max_attempts)


def base62_encode(num):
    """
    Encode a number to base62 (using alphanumeric characters)
    Useful for creating short codes from sequential IDs
    
    Args:
        num: Integer to encode
    
    Returns:
        Base62 encoded string
    """
    if num == 0:
        return '0'
    
    base62_chars = string.digits + string.ascii_lowercase + string.ascii_uppercase
    encoded = []
    
    while num:
        num, remainder = divmod(num, 62)
        encoded.append(base62_chars[remainder])
    
    return ''.join(reversed(encoded))


def is_valid_custom_code(code):
    """
    Validate a custom short code
    
    Args:
        code: The custom code to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return False, "Short code cannot be empty"
    
    if len(code) < 3:
        return False, "Short code must be at least 3 characters long"
    
    if len(code) > 20:
        return False, "Short code must be at most 20 characters long"
    
    # Only allow alphanumeric characters and hyphens
    allowed_chars = string.ascii_letters + string.digits + '-_'
    if not all(c in allowed_chars for c in code):
        return False, "Short code can only contain letters, numbers, hyphens, and underscores"
    
    # Reserved words that shouldn't be used as short codes
    reserved = ['admin', 'api', 'login', 'logout', 'register', 'dashboard', 'static', 'media', 'url']
    if code.lower() in reserved:
        return False, f"'{code}' is a reserved word and cannot be used"
    
    return True, ""


def get_client_ip(request):
    """
    Get the client's IP address from the request
    
    Args:
        request: Django request object
    
    Returns:
        IP address string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_url(url):
    """
    Format a URL to ensure it has a proper scheme
    
    Args:
        url: URL string
    
    Returns:
        Properly formatted URL with http:// or https://
    """
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url