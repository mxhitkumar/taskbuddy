# Service Marketplace API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All protected endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 🔐 User & Authentication Endpoints

### 1. Register User
**POST** `/users/register/`

Creates a new user account.

**Request Body:**
```json
{
  "email": "john@example.com",
  "phone": "+1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "CUSTOMER",  // CUSTOMER, SERVICE_PROVIDER, ADMIN
  "profile": {
    "city": "New York",
    "state": "NY",
    "country": "USA"
  },
  "provider_profile": {  // Required only for SERVICE_PROVIDER role
    "business_name": "John's Plumbing",
    "business_description": "Professional plumbing services",
    "years_of_experience": 5
  }
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "role": "CUSTOMER",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

### 2. Login
**POST** `/users/login/`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "user": { ... },
  "tokens": {
    "refresh": "...",
    "access": "..."
  },
  "message": "Login successful"
}
```

### 3. Refresh Token
**POST** `/users/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Get User Profile
**GET** `/users/profile/`
*Requires Authentication*

### 5. Update User Profile
**PUT** `/users/profile/`
*Requires Authentication*

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe Updated",
  "phone": "+1234567890",
  "profile": {
    "bio": "Experienced professional",
    "city": "Los Angeles",
    "state": "CA"
  }
}
```

### 6. Change Password
**POST** `/users/password/change/`
*Requires Authentication*

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```

### 7. Request Password Reset
**POST** `/users/password/reset/request/`

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

### 8. Confirm Password Reset
**POST** `/users/password/reset/confirm/`

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp_code": "123456",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```

### 9. List Service Providers
**GET** `/users/providers/?verified=true&city=NewYork&search=plumber`
*Requires Authentication*

**Query Parameters:**
- `verified` (boolean): Filter verified providers
- `city` (string): Filter by city
- `search` (string): Search by name or business name

### 10. Verify Provider (Admin Only)
**PUT** `/users/providers/{id}/verify/`
*Requires Admin Authentication*

**Request Body:**
```json
{
  "verification_status": "VERIFIED"  // PENDING, UNDER_REVIEW, VERIFIED, REJECTED
}
```

---

## 🛠️ Service Endpoints

### 1. List Service Categories
**GET** `/services/categories/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Plumbing",
    "slug": "plumbing",
    "description": "Plumbing services",
    "icon": "/media/categories/plumbing.png",
    "service_count": 45,
    "provider_count": 12,
    "subcategories": [
      {
        "id": 2,
        "name": "Emergency Plumbing",
        "slug": "emergency-plumbing",
        ...
      }
    ]
  }
]
```

### 2. List Services
**GET** `/services/?category=1&min_price=50&max_price=200&city=NewYork&verified_only=true`

**Query Parameters:**
- `category` (int): Filter by category ID
- `min_price` (decimal): Minimum price
- `max_price` (decimal): Maximum price
- `city` (string): Filter by city
- `state` (string): Filter by state
- `min_rating` (decimal): Minimum rating (1-5)
- `pricing_type` (string): FIXED, HOURLY, CUSTOM
- `is_featured` (boolean): Featured services only
- `verified_only` (boolean): Verified providers only
- `search` (string): Search in title/description
- `ordering` (string): created_at, -created_at, average_rating, -average_rating, base_price, -base_price

**Response:** `200 OK`
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/services/?page=2",
  "previous": null,
  "total_pages": 8,
  "current_page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "slug": "expert-plumbing-service",
      "title": "Expert Plumbing Service",
      "short_description": "Fast and reliable plumbing",
      "thumbnail": "/media/services/thumbnails/plumbing.jpg",
      "category": 1,
      "category_name": "Plumbing",
      "provider": 5,
      "provider_name": "John Doe",
      "pricing_type": "HOURLY",
      "pricing_type_display": "Hourly Rate",
      "base_price": "75.00",
      "currency": "USD",
      "duration_minutes": 120,
      "is_featured": false,
      "average_rating": "4.50",
      "review_count": 28,
      "booking_count": 45,
      "created_at": "2025-10-15T10:30:00Z"
    }
  ]
}
```

### 3. Get Service Details
**GET** `/services/{slug}/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "slug": "expert-plumbing-service",
  "title": "Expert Plumbing Service",
  "description": "Comprehensive plumbing services including...",
  "short_description": "Fast and reliable plumbing",
  "thumbnail": "/media/services/thumbnails/plumbing.jpg",
  "images": [
    {
      "id": 1,
      "image": "/media/services/images/img1.jpg",
      "caption": "Work sample",
      "order": 0
    }
  ],
  "category": {
    "id": 1,
    "name": "Plumbing",
    "slug": "plumbing"
  },
  "provider": {
    "id": 5,
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "SERVICE_PROVIDER",
    "provider_profile": {
      "business_name": "John's Plumbing",
      "average_rating": "4.75",
      "total_reviews": 52,
      "verification_status": "VERIFIED"
    }
  },
  "pricing_type": "HOURLY",
  "base_price": "75.00",
  "currency": "USD",
  "duration_minutes": 120,
  "average_rating": "4.50",
  "review_count": 28,
  "view_count": 1250,
  "booking_count": 45
}
```

### 4. Create Service (Provider Only)
**POST** `/services/create/`
*Requires Provider Authentication*

**Request Body:**
```json
{
  "title": "Expert Plumbing Service",
  "slug": "expert-plumbing-service",
  "description": "Comprehensive plumbing services...",
  "short_description": "Fast and reliable plumbing",
  "category": 1,
  "pricing_type": "HOURLY",
  "base_price": "75.00",
  "currency": "USD",
  "duration_minutes": 120,
  "meta_title": "Expert Plumbing in NYC",
  "meta_description": "Professional plumbing services..."
}
```

### 5. Update Service
**PUT** `/services/{slug}/update/`
*Requires Provider Authentication (own services only)*

### 6. Delete Service
**DELETE** `/services/{slug}/delete/`
*Requires Provider Authentication (own services only)*

### 7. My Services (Provider)
**GET** `/services/my-services/`
*Requires Provider Authentication*

### 8. Featured Services
**GET** `/services/featured/`

### 9. Popular Services
**GET** `/services/popular/`

### 10. Manage Availability (Provider)
**GET/POST** `/services/availability/`
*Requires Provider Authentication*

**POST Request Body:**
```json
{
  "day_of_week": 0,  // 0=Monday, 6=Sunday
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "is_available": true
}
```

### 11. Manage Service Areas (Provider)
**GET/POST** `/services/areas/`
*Requires Provider Authentication*

**POST Request Body:**
```json
{
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "service_radius_km": 15,
  "is_active": true
}
```

---

## 📅 Booking Endpoints

### 1. List Bookings
**GET** `/bookings/?status=CONFIRMED&start_date=2025-11-01&end_date=2025-11-30`
*Requires Authentication*

**Query Parameters:**
- `status` (string): PENDING, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, REFUNDED
- `start_date` (date): Filter by scheduled date (from)
- `end_date` (date): Filter by scheduled date (to)

**Response:** `200 OK`
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "booking_reference": "BK1A2B3C4D5E",
      "status": "CONFIRMED",
      "status_display": "Confirmed",
      "customer": 10,
      "customer_name": "Jane Smith",
      "provider": 5,
      "provider_name": "John Doe",
      "service": 1,
      "service_title": "Expert Plumbing Service",
      "scheduled_date": "2025-11-15",
      "scheduled_time": "10:00:00",
      "total_amount": "150.00",
      "currency": "USD",
      "created_at": "2025-10-20T14:30:00Z"
    }
  ]
}
```

### 2. Get Booking Details
**GET** `/bookings/{booking_reference}/`
*Requires Authentication*

**Response:** `200 OK`
```json
{
  "id": 1,
  "booking_reference": "BK1A2B3C4D5E",
  "customer": { ... },
  "provider": { ... },
  "service": { ... },
  "status": "CONFIRMED",
  "scheduled_date": "2025-11-15",
  "scheduled_time": "10:00:00",
  "estimated_duration_minutes": 120,
  "service_address": "123 Main St, Apt 4B",
  "service_city": "New York",
  "service_state": "NY",
  "service_postal_code": "10001",
  "base_price": "150.00",
  "additional_charges": "0.00",
  "tax_amount": "15.00",
  "discount_amount": "0.00",
  "total_amount": "165.00",
  "currency": "USD",
  "customer_notes": "Please ring doorbell twice",
  "confirmed_at": "2025-10-20T15:00:00Z",
  "created_at": "2025-10-20T14:30:00Z"
}
```

### 3. Create Booking (Customer Only)
**POST** `/bookings/create/`
*Requires Customer Authentication*

**Request Body:**
```json
{
  "service": 1,
  "scheduled_date": "2025-11-15",
  "scheduled_time": "10:00:00",
  "estimated_duration_minutes": 120,
  "service_address": "123 Main St, Apt 4B",
  "service_city": "New York",
  "service_state": "NY",
  "service_postal_code": "10001",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "customer_notes": "Please ring doorbell twice"
}
```

**Response:** `201 Created`

### 4. Update Booking Details
**PUT** `/bookings/{booking_reference}/update/`
*Requires Customer Authentication (only pending/confirmed bookings)*

### 5. Update Booking Status
**POST** `/bookings/{booking_reference}/status/`
*Requires Authentication*

**Request Body:**
```json
{
  "status": "CONFIRMED",
  "notes": "Confirmed and scheduled"
}
```

**Allowed Status Transitions:**
- PENDING → CONFIRMED, CANCELLED
- CONFIRMED → IN_PROGRESS, CANCELLED
- IN_PROGRESS → COMPLETED, CANCELLED
- CANCELLED → REFUNDED

### 6. Cancel Booking
**POST** `/bookings/{booking_reference}/cancel/`
*Requires Authentication*

**Request Body:**
```json
{
  "cancellation_reason": "Change of plans"
}
```

### 7. Upload Booking Attachments
**POST** `/bookings/{booking_reference}/attachments/`
*Requires Authentication*

**Form Data:**
```
file: [binary file]
description: "Before photo"
```

### 8. Get Booking Attachments
**GET** `/bookings/{booking_reference}/attachments/`

### 9. Get Booking History
**GET** `/bookings/{booking_reference}/history/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "from_status": "PENDING",
    "to_status": "CONFIRMED",
    "changed_by": 5,
    "changed_by_name": "John Doe",
    "notes": "Confirmed by provider",
    "created_at": "2025-10-20T15:00:00Z"
  }
]
```

---

## ⭐ Review Endpoints

### 1. List Reviews
**GET** `/reviews/?provider=5&service=1&min_rating=4&order=helpful`

**Query Parameters:**
- `provider` (int): Filter by provider ID
- `service` (int): Filter by service ID
- `min_rating` (int): Minimum rating (1-5)
- `order` (string): -created_at (default), helpful, rating_high, rating_low

### 2. Get Review Details
**GET** `/reviews/{id}/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "booking": 1,
  "customer": 10,
  "customer_name": "Jane Smith",
  "customer_avatar": "/media/avatars/jane.jpg",
  "provider": 5,
  "provider_name": "John Doe",
  "service": 1,
  "service_title": "Expert Plumbing Service",
  "rating": 5,
  "title": "Excellent Service!",
  "comment": "Very professional and completed the job perfectly. Highly recommend!",
  "quality_rating": 5,
  "punctuality_rating": 5,
  "professionalism_rating": 5,
  "value_rating": 5,
  "is_verified": true,
  "helpful_count": 12,
  "images": [
    {
      "id": 1,
      "image": "/media/reviews/images/review1.jpg",
      "caption": "After repair"
    }
  ],
  "response": {
    "id": 1,
    "provider": 5,
    "provider_name": "John Doe",
    "response_text": "Thank you for the kind words!",
    "created_at": "2025-10-22T10:00:00Z"
  },
  "created_at": "2025-10-21T16:30:00Z"
}
```

### 3. Create Review (Customer Only)
**POST** `/reviews/create/`
*Requires Customer Authentication (for completed bookings only)*

**Request Body:**
```json
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

### 4. Update Review
**PUT** `/reviews/{id}/update/`
*Requires Customer Authentication (own reviews only)*

### 5. Delete Review
**DELETE** `/reviews/{id}/delete/`
*Requires Customer Authentication (own reviews only)*

### 6. My Reviews
**GET** `/reviews/my-reviews/`
*Requires Customer Authentication*

### 7. Provider Reviews
**GET** `/reviews/provider/{provider_id}/`

### 8. Service Reviews
**GET** `/reviews/service/{service_id}/`

### 9. Respond to Review (Provider Only)
**POST** `/reviews/{review_id}/respond/`
*Requires Provider Authentication*

**Request Body:**
```json
{
  "response_text": "Thank you for the kind words! It was a pleasure working with you."
}
```

### 10. Mark Review as Helpful
**POST** `/reviews/{review_id}/helpful/`
*Requires Authentication*

**Request Body:**
```json
{
  "helpful": true  // true to mark, false to unmark
}
```

### 11. Review Statistics
**GET** `/reviews/stats/?provider=5` or `/reviews/stats/?service=1`

**Response:** `200 OK`
```json
{
  "total_reviews": 52,
  "average_rating": 4.65,
  "average_quality": 4.70,
  "average_punctuality": 4.60,
  "average_professionalism": 4.75,
  "average_value": 4.55,
  "rating_distribution": {
    "5_star": 35,
    "4_star": 12,
    "3_star": 3,
    "2_star": 1,
    "1_star": 1
  }
}
```

---

## 📊 Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "status_code": 400,
    "details": {
      "field_name": ["Error message"]
    }
  }
}
```

### Common HTTP Status Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request (resource created)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## 🔄 Pagination

List endpoints return paginated results:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/services/?page=2",
  "previous": null,
  "total_pages": 8,
  "current_page": 1,
  "page_size": 20,
  "results": [...]
}
```

**Query Parameters:**
- `page` (int): Page number
- `page_size` (int): Items per page (max: 100)

---

## 🎯 Rate Limiting

- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Booking operations: 50 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1635782400
```