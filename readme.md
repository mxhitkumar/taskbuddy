# Service Marketplace Platform

A scalable service marketplace platform for booking local workers (plumbers, electricians, cooks, maids) built with Django REST Framework and React. Designed to handle 1 million+ concurrent users with optimized database design and high-performance architecture.

## 🚀 Features

### Core Functionality
- **Multi-Role Authentication**: Superadmin, Admin, Service Provider, Customer
- **Service Management**: Create, update, and manage service listings
- **Booking System**: Complete booking lifecycle management
- **Review & Rating**: Customer reviews with detailed sub-ratings
- **Real-time Notifications**: Email notifications for booking updates
- **Provider Verification**: Admin workflow for verifying service providers

### Technical Highlights
- JWT-based authentication with role-based access control
- PostgreSQL with optimized indexing for high performance
- Redis caching for frequently accessed data
- Celery for asynchronous task processing
- RESTful API with comprehensive documentation
- Docker containerization for easy deployment
- Horizontal scaling ready architecture

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Method 1: Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd marketplace
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Run Celery worker (in separate terminal)**
```bash
celery -A config worker -l info
```

9. **Run Celery beat (in separate terminal)**
```bash
celery -A config beat -l info
```

### Method 2: Docker Deployment

1. **Build and start containers**
```bash
docker-compose up --build
```

2. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

3. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📚 API Documentation

Once the server is running, access:
- Swagger UI: `http://localhost:8000/api/docs/`
- API Schema: `http://localhost:8000/api/schema/`

### Authentication Endpoints

#### Register User
```http
POST /api/users/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "phone": "+1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "CUSTOMER"
}
```

#### Login
```http
POST /api/users/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Refresh Token
```http
POST /api/users/token/refresh/
Content-Type: application/json

{
  "refresh": "your-refresh-token"
}
```

### Service Endpoints

#### List Services
```http
GET /api/services/?category=1&min_price=50&max_price=200&city=NewYork
Authorization: Bearer <access-token>
```

#### Create Service (Provider only)
```http
POST /api/services/create/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "title": "Expert Plumbing Service",
  "slug": "expert-plumbing-service",
  "description": "Professional plumbing services...",
  "short_description": "Fast and reliable plumbing",
  "category": 1,
  "pricing_type": "HOURLY",
  "base_price": "75.00",
  "currency": "USD",
  "duration_minutes": 120
}
```

### Booking Endpoints

#### Create Booking
```http
POST /api/bookings/create/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "service": 1,
  "scheduled_date": "2025-11-01",
  "scheduled_time": "10:00:00",
  "estimated_duration_minutes": 120,
  "service_address": "123 Main St, Apt 4B",
  "service_city": "New York",
  "service_state": "NY",
  "service_postal_code": "10001",
  "customer_notes": "Please ring doorbell twice"
}
```

#### Update Booking Status
```http
POST /api/bookings/{booking_reference}/status/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "status": "CONFIRMED",
  "notes": "Confirmed and ready to proceed"
}
```

### Review Endpoints

#### Create Review
```http
POST /api/reviews/create/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "booking": 1,
  "rating": 5,
  "title": "Excellent Service!",
  "comment": "Very professional and completed the job perfectly.",
  "quality_rating": 5,
  "punctuality_rating": 5,
  "professionalism_rating": 5,
  "value_rating": 5
}
```

## 🏗️ Architecture

### Database Schema

The platform uses PostgreSQL with the following key tables:
- **users**: Custom user model with role-based access
- **user_profiles**: Extended user information
- **service_provider_profiles**: Provider-specific data with verification status
- **services**: Service listings with denormalized statistics
- **service_categories**: Hierarchical category structure
- **bookings**: Booking records with complete lifecycle tracking
- **reviews**: Customer reviews with sub-ratings
- **booking_status_history**: Audit trail for all status changes

### Performance Optimizations

1. **Database Indexing**: Strategic indexes on frequently queried fields
2. **Query Optimization**: Select_related and prefetch_related for complex queries
3. **Caching**: Redis caching for categories, featured services, and statistics
4. **Denormalization**: Cached counts and averages to avoid expensive aggregations
5. **Async Processing**: Celery tasks for emails, notifications, and heavy operations
6. **Connection Pooling**: PostgreSQL connection pooling for better resource utilization

### Scalability Features

- **Horizontal Scaling**: Stateless application design
- **Load Balancing**: Nginx reverse proxy with upstream configuration
- **Cache Layer**: Redis for session management and data caching
- **Task Queue**: Celery with Redis broker for distributed task processing
- **Database Read Replicas**: Ready for read/write splitting
- **CDN Ready**: Static and media files can be served via CDN

## 🔒 Security Features

- Argon2 password hashing
- JWT token-based authentication
- Role-based access control (RBAC)
- CORS configuration
- SQL injection protection via ORM
- XSS protection headers
- CSRF protection
- Rate limiting on API endpoints

## 📊 Monitoring & Logging

- Structured logging with rotation
- Celery task monitoring
- Database query logging (in development)
- Error tracking ready (Sentry integration available)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific app tests
pytest apps/users/tests.py
```

## 📦 Deployment

### Production Settings

1. Update `config/settings/production.py`:
   - Set DEBUG = False
   - Configure ALLOWED_HOSTS
   - Set up proper SECRET_KEY
   - Configure email backend
   - Set up S3 for file storage (optional)

2. Use environment variables for sensitive data

3. Run with Gunicorn:
```bash
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

### Docker Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔄 Database Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## 📝 API Rate Limits

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Booking creation: 50 requests/hour

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For support, email support@marketplace.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Real-time chat between customers and providers
- [ ] Payment gateway integration
- [ ] Mobile app (React Native)
- [ ] Advanced search with Elasticsearch
- [ ] AI-powered service recommendations
- [ ] Multi-language support
- [ ] Provider analytics dashboard