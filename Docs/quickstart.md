# Quick Start Guide - Service Marketplace Platform

Get your service marketplace running in 5 minutes!

## 🚀 Option 1: Docker (Recommended - Fastest)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd marketplace

# 2. Create environment file
cp .env.example .env

# 3. Start everything
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create admin user
docker-compose exec web python manage.py createsuperuser

# 6. Access the application
# API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/docs/
```

✅ **Done!** Your marketplace is running.

---

## 💻 Option 2: Local Development

```bash
# 1. Prerequisites
# - Python 3.11+
# - PostgreSQL 15+
# - Redis 7+

# 2. Clone and setup
git clone <your-repo-url>
cd marketplace
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
# Create PostgreSQL database: marketplace
createdb marketplace

# 5. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Start services
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A config worker -l info

# Terminal 3: Celery Beat
celery -A config beat -l info

# 9. Access
# API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/docs/
```

---

## 📝 First API Call

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "phone": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "role": "CUSTOMER"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Get Services (with token)

```bash
curl -X GET http://localhost:8000/api/services/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎯 Test the Platform

### Using Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Create Service Categories (Plumbing, Electrical, etc.)
4. Create Service Providers
5. Verify providers
6. Create services

### Using API Documentation

1. Go to `http://localhost:8000/api/docs/`
2. Explore all endpoints
3. Test API calls directly from browser

---

## 📊 Sample Data Script

Create `scripts/load_sample_data.py`:

```python
from django.contrib.auth import get_user_model
from services.models import ServiceCategory, Service
from users.models import ServiceProviderProfile

User = get_user_model()

# Create service provider
provider = User.objects.create_user(
    email='plumber@example.com',
    password='pass123',
    first_name='John',
    last_name='Plumber',
    phone='+1234567890',
    role='SERVICE_PROVIDER',
    is_verified=True
)

# Create provider profile
ServiceProviderProfile.objects.create(
    user=provider,
    business_name="John's Plumbing Services",
    business_description="Expert plumbing services",
    years_of_experience=10,
    verification_status='VERIFIED'
)

# Create category
category = ServiceCategory.objects.create(
    name='Plumbing',
    slug='plumbing',
    is_active=True
)

# Create service
Service.objects.create(
    title='Emergency Plumbing',
    slug='emergency-plumbing',
    description='24/7 emergency plumbing services',
    short_description='Fast emergency repairs',
    provider=provider,
    category=category,
    pricing_type='HOURLY',
    base_price=75.00,
    currency='USD',
    duration_minutes=120,
    is_active=True
)

print("Sample data created successfully!")
```

Run it:
```bash
python manage.py shell < scripts/load_sample_data.py
```

---

## 🔍 Common Commands

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Admin
python manage.py createsuperuser
python manage.py changepassword username

# Shell
python manage.py shell
python manage.py shell_plus  # if django-extensions installed

# Static files
python manage.py collectstatic

# Tests
pytest
pytest --cov=apps

# Celery
celery -A config worker -l info
celery -A config beat -l info
celery -A config flower  # monitoring UI

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose exec web python manage.py migrate
```

---

## 📱 Test Workflow

### Complete User Journey

1. **Register Customer**
   ```bash
   POST /api/users/register/
   ```

2. **Login**
   ```bash
   POST /api/users/login/
   ```

3. **Browse Services**
   ```bash
   GET /api/services/?category=1&city=NewYork
   ```

4. **View Service Details**
   ```bash
   GET /api/services/emergency-plumbing/
   ```

5. **Create Booking**
   ```bash
   POST /api/bookings/create/
   {
     "service": 1,
     "scheduled_date": "2025-11-01",
     "scheduled_time": "10:00:00",
     ...
   }
   ```

6. **Provider Confirms**
   ```bash
   POST /api/bookings/BK123456/status/
   {
     "status": "CONFIRMED"
   }
   ```

7. **Service Completed**
   ```bash
   POST /api/bookings/BK123456/status/
   {
     "status": "COMPLETED"
   }
   ```

8. **Customer Reviews**
   ```bash
   POST /api/reviews/create/
   {
     "booking": 1,
     "rating": 5,
     "title": "Excellent!",
     ...
   }
   ```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo service postgresql status
# or
pg_isready
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis
sudo service redis-server start
```

### Celery Not Processing Tasks
```bash
# Check Celery worker is running
ps aux | grep celery

# Restart worker
celery -A config worker -l info
```

### Import Errors
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Migration Errors
```bash
# Reset database (WARNING: destroys data)
python manage.py flush
python manage.py migrate

# Or delete and recreate database
dropdb marketplace
createdb marketplace
python manage.py migrate
```

---

## 📚 Next Steps

### 1. Customize Configuration
- Update `.env` with real credentials
- Configure email service (SendGrid/AWS SES)
- Set up AWS S3 for file storage
- Configure domain and SSL

### 2. Add More Features
- Payment integration (Stripe/PayPal)
- Real-time chat (Django Channels)
- Push notifications (FCM)
- Advanced analytics dashboard
- Multi-language support

### 3. Deploy to Production
- Follow `DEPLOYMENT_GUIDE.md`
- Set up monitoring (Sentry, New Relic)
- Configure backups
- Set up CI/CD pipeline

### 4. Performance Optimization
- Enable database query logging
- Monitor slow queries
- Optimize cache strategy
- Set up CDN for static files

---

## 🎓 Learning Resources

### Understand the Architecture
```
marketplace/
├── apps/                    # All Django apps
│   ├── users/              # Authentication & user management
│   ├── services/           # Service listings
│   ├── bookings/           # Booking system
│   └── reviews/            # Rating & reviews
├── config/                 # Project configuration
│   ├── settings/           # Environment-based settings
│   ├── urls.py            # URL routing
│   └── celery.py          # Async tasks
└── core/                   # Shared utilities
```

### Key Concepts
- **Models**: Database structure (ORM)
- **Serializers**: Data validation & transformation
- **Views**: Business logic & API endpoints
- **Permissions**: Access control
- **Signals**: Automatic actions on events
- **Tasks**: Background jobs (Celery)

### API Structure
```
/api/users/          # User & authentication
/api/services/       # Service management
/api/bookings/       # Booking operations
/api/reviews/        # Reviews & ratings
```

---

## 🔐 Default Credentials

After running `createsuperuser`, you'll have:
- **Email**: (your input)
- **Password**: (your input)
- **Role**: SUPERADMIN

### Test Accounts (if using sample data script)
```
Provider:
- Email: plumber@example.com
- Password: pass123
- Role: SERVICE_PROVIDER

Customer:
- Email: customer@example.com
- Password: pass123
- Role: CUSTOMER
```

---

## 📊 Monitoring URLs

Once running, access these:

| Service | URL | Description |
|---------|-----|-------------|
| API Docs | http://localhost:8000/api/docs/ | Swagger UI |
| Admin Panel | http://localhost:8000/admin/ | Django admin |
| API Schema | http://localhost:8000/api/schema/ | OpenAPI schema |
| Health Check | http://localhost:8000/api/health/ | Status check |

---

## 💡 Pro Tips

### 1. Use Makefile for Common Tasks
```bash
make install         # Install dependencies
make migrate         # Run migrations
make run            # Start dev server
make celery         # Start Celery worker
make test           # Run tests
```

### 2. Enable Debug Toolbar (Development)
```python
# Already configured in development settings
# Just visit any page and see the debug toolbar
```

### 3. Use Django Shell Plus
```bash
pip install django-extensions
python manage.py shell_plus
# Auto-imports all models
```

### 4. Database Inspection
```bash
# Access database
python manage.py dbshell

# View all tables
\dt

# Describe table
\d users
```

### 5. Quick Data Inspection
```bash
# Django shell
python manage.py shell

>>> from users.models import User
>>> User.objects.count()
>>> User.objects.filter(role='SERVICE_PROVIDER').count()
```

---

## 🎯 Development Workflow

### Feature Development
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# ... edit code ...

# 3. Run tests
pytest

# 4. Check migrations
python manage.py makemigrations --dry-run

# 5. Create migrations
python manage.py makemigrations

# 6. Apply migrations
python manage.py migrate

# 7. Test locally
python manage.py runserver

# 8. Commit and push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### Code Quality
```bash
# Format code (if using black)
black apps/

# Check linting (if using flake8)
flake8 apps/

# Type checking (if using mypy)
mypy apps/
```

---

## 🚦 Environment-Specific Settings

### Development (Default)
```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver
```

### Production
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn config.wsgi:application
```

### Testing
```bash
export DJANGO_SETTINGS_MODULE=config.settings.testing
pytest
```

---

## 📞 Getting Help

### Check Logs
```bash
# Application logs
tail -f logs/django.log

# Celery logs
tail -f logs/celery.log

# Docker logs
docker-compose logs -f web
```

### Common Error Solutions

**Error: "No module named 'apps'"**
```bash
# Make sure you're in project root
pwd
# Should show: /path/to/marketplace

# Activate virtual environment
source venv/bin/activate
```

**Error: "relation does not exist"**
```bash
# Run migrations
python manage.py migrate
```

**Error: "CSRF token missing"**
```bash
# For API calls, include CSRF token or use JWT authentication
# JWT is already configured, use Bearer token
```

---

## 🎉 Success Checklist

After setup, verify everything works:

- [ ] ✅ Server starts without errors
- [ ] ✅ Can access admin panel
- [ ] ✅ Can register new user via API
- [ ] ✅ Can login and get JWT token
- [ ] ✅ Can create service category (admin)
- [ ] ✅ Can create service (provider)
- [ ] ✅ Can browse services (customer)
- [ ] ✅ Can create booking (customer)
- [ ] ✅ Can update booking status (provider)
- [ ] ✅ Can leave review (customer)
- [ ] ✅ Celery processes tasks
- [ ] ✅ Email notifications work (check console)
- [ ] ✅ API documentation is accessible

---

## 📖 Additional Documentation

- **API Documentation**: See `API_DOCUMENTATION.md`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **Complete Checklist**: See `COMPLETE_FILE_CHECKLIST.md`
- **Main README**: See `README.md`

---

## 🚀 You're Ready!

Your service marketplace platform is now running with:
- ✅ 4 user roles
- ✅ Complete booking system
- ✅ Review & rating system
- ✅ Background task processing
- ✅ Email notifications
- ✅ Scalable architecture
- ✅ Production-ready code

**Start building your marketplace! 🎊**

---

## 💬 Support

For issues or questions:
- 📧 Email: support@marketplace.com
- 🐛 Issues: GitHub Issues
- 📚 Docs: All documentation files in repository

**Happy coding! 🚀**