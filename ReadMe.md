# URL Shortener - Django Application

A feature-rich URL shortening service built with Django that allows users to create, manage, and track shortened URLs.

## Features

### Core Features ✅
- **User Authentication**: Complete registration, login, and logout system
- **URL Shortening**: Convert long URLs into short, shareable links
- **Custom Short Codes**: Option to create custom memorable short codes
- **URL Management**: View, edit, and delete your shortened URLs
- **Click Analytics**: Track click counts and view detailed statistics
- **Search & Filter**: Search URLs and sort by various criteria

### Bonus Features ✅
- **QR Code Generation**: Generate QR codes for any shortened URL
- **Expiration Dates**: Set expiration times for URLs (up to 365 days)
- **Detailed Analytics**: View clicks by date, IP addresses, and user agents
- **Active/Inactive Toggle**: Temporarily disable URLs without deleting them
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5

## Technology Stack

- **Backend**: Django 5.0+
- **Database**: PostgreSQL (with SQLite fallback)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Authentication**: Django built-in auth system
- **QR Codes**: qrcode library with Pillow

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- PostgreSQL (optional, SQLite works as fallback)
- pip and virtualenv

### Step 1: Clone the Repository
```bash
cd ~/Desktop/url_shortener
# Your project is already here
```

### Step 2: Install Dependencies
```bash
# Make sure you're in your virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Create a `.env` file in the project root directory:

```bash
# .env file
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Configuration (Optional - remove these to use SQLite)
DB_NAME=url_shortener_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

**Note**: If you don't have PostgreSQL, just don't set the DB_* variables and the app will use SQLite automatically.

### Step 4: Setup Database

For **SQLite** (easier, default):
```bash
python manage.py makemigrations
python manage.py migrate
```

For **PostgreSQL** (if you have it):
```bash
# First create the database
psql -U postgres
CREATE DATABASE url_shortener_db;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE url_shortener_db TO your_db_user;
\q

# Then run migrations
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 6: Run the Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

## File Structure

```
url_shortener/
├── manage.py
├── requirements.txt
├── .env
├── db.sqlite3
├── url_manager/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── shortener/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── utils.py
│   ├── migrations/
│   └── templates/
│       └── shortener/
│           ├── base.html
│           ├── home.html
│           ├── login.html
│           ├── register.html
│           ├── dashboard.html
│           ├── create_url.html
│           ├── url_detail.html
│           ├── edit_url.html
│           ├── delete_url.html
│           ├── analytics.html
│           ├── url_inactive.html
│           └── url_expired.html
├── static/
└── venv/
```

## Usage Guide

### 1. Register an Account
- Navigate to the home page
- Click "Register" or "Get Started"
- Fill in username, email, and password
- You'll be automatically logged in

### 2. Create a Short URL
- Click "Create Short URL" in the navigation
- Enter your long URL
- (Optional) Add a description
- (Optional) Create a custom short code
- (Optional) Set an expiration date
- Click "Create Short URL"

### 3. Manage URLs
- View all your URLs in the Dashboard
- Use search to find specific URLs
- Sort by date, clicks, or short code
- Edit, view analytics, generate QR codes, or delete URLs

### 4. Track Analytics
- Click on any URL to view details
- See total clicks, creation date, and expiration
- View recent clicks with IP addresses
- Access detailed analytics with daily breakdowns

### 5. Generate QR Codes
- Click the QR code button on any URL
- Download the QR code image
- Use it for print materials or mobile sharing

## API Endpoints

- `/` - Home page
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/dashboard/` - User dashboard
- `/create/` - Create new short URL
- `/url/<short_code>/` - View URL details
- `/url/<short_code>/edit/` - Edit URL
- `/url/<short_code>/delete/` - Delete URL
- `/url/<short_code>/analytics/` - View analytics
- `/url/<short_code>/qr/` - Generate QR code
- `/<short_code>/` - Redirect to original URL

## Key Features Implementation

### URL Shortening Algorithm
- Uses base62 encoding (alphanumeric characters)
- Generates 6-character codes by default
- Ensures uniqueness by checking database
- Supports custom codes with validation

### Analytics Tracking
- Records every click with timestamp
- Captures IP address and user agent
- Provides daily click aggregation
- Shows recent click history

### Security Features
- User authentication required for URL management
- CSRF protection on all forms
- Password validation
- SQL injection prevention via Django ORM

## Admin Panel

Access the admin panel at `/admin/` with superuser credentials:
- Manage users
- View all shortened URLs
- Monitor click analytics
- Moderate content

## Deployment Checklist

Before deploying to production:

1. Set `DEBUG=False` in settings
2. Use a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` properly
4. Use PostgreSQL for production
5. Set up static file serving
6. Configure HTTPS
7. Set up proper logging
8. Use environment variables for sensitive data

## Troubleshooting

### Database Issues
- If migrations fail, delete `db.sqlite3` and migration files, then run `makemigrations` and `migrate` again
- For PostgreSQL connection issues, check your credentials in `.env`

### QR Code Generation
- Ensure Pillow is installed: `pip install Pillow`
- Check that the media directory is writable

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Ensure `STATIC_ROOT` is configured

## Future Enhancements

Potential features for future versions:
- Password-protected URLs
- Link preview/thumbnail generation
- Bulk URL creation via CSV
- API for programmatic access
- Advanced analytics (geographic location, device type)
- URL categorization and tagging
- Team collaboration features
- Custom domains

## Contributing

This is a task submission project. However, suggestions and feedback are welcome!

## License

This project is created for educational purposes as part of a developer interview task.

## Contact

For questions or issues, please contact the developer.

---

**Happy URL Shortening! 🚀**