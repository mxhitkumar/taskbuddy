# 🚀 Postman Collection - Service Marketplace API

## 📦 What's Included

This Postman collection contains **50+ API endpoints** fully configured and ready to test the entire Service Marketplace platform.

### ✨ Features

- ✅ **Auto-saves tokens** after login
- ✅ **Auto-sets booking references** after creation
- ✅ **Auto-updates service slugs** for easy testing
- ✅ **Pre-configured with sample data**
- ✅ **Works out of the box** - no manual token copying
- ✅ **Complete workflow** from registration to review
- ✅ **Organized in logical folders**
- ✅ **Environment variables** for easy switching

---

## 🎯 Quick Import (30 seconds)

### Step 1: Copy JSON
Copy the entire JSON content from the `Service Marketplace - Postman Collection` artifact above.

### Step 2: Import to Postman
1. Open Postman
2. Click **Import** (top left)
3. Select **Raw text** tab
4. Paste JSON
5. Click **Import**

### Step 3: Setup Environment
1. Click **Environments** (left sidebar)
2. Create new: "Marketplace Local"
3. Add variable:
   - Name: `base_url`
   - Value: `http://localhost:8000`
4. **Save** and **Select** this environment

### Step 4: Start Testing!
✅ You're ready to test all APIs!

---

## 📋 Collection Structure

```
📁 Service Marketplace API (50+ endpoints)
│
├── 📁 Authentication (4 endpoints)
│   ├── Register Customer
│   ├── Register Service Provider
│   ├── Login ⭐ (Auto-saves token)
│   └── Refresh Token
│
├── 📁 User Profile (5 endpoints)
│   ├── Get My Profile
│   ├── Update Profile
│   ├── Change Password
│   ├── Request Password Reset
│   └── List Service Providers
│
├── 📁 Service Categories (1 endpoint)
│   └── List Categories
│
├── 📁 Services (9 endpoints)
│   ├── List Services
│   ├── Search Services
│   ├── Get Service Details
│   ├── Create Service ⭐ (Auto-saves slug)
│   ├── Update Service
│   ├── My Services
│   ├── Featured Services
│   └── Popular Services
│
├── 📁 Bookings (8 endpoints)
│   ├── Create Booking ⭐ (Auto-saves reference)
│   ├── List Bookings
│   ├── Get Booking Details
│   ├── Update Status - Confirm
│   ├── Update Status - In Progress
│   ├── Update Status - Completed
│   ├── Cancel Booking
│   └── Get Booking History
│
└── 📁 Reviews (9 endpoints)
    ├── Create Review
    ├── List Reviews
    ├── Get Review Details
    ├── Provider Reviews
    ├── Service Reviews
    ├── My Reviews
    ├── Respond to Review
    ├── Mark as Helpful
    └── Review Statistics
```

---

## 🎬 5-Minute Quick Test

Follow this exact sequence to test complete platform:

### 1️⃣ Register Users (30 sec)
```
POST Authentication → Register Customer
POST Authentication → Register Service Provider
```

### 2️⃣ Create Service (30 sec)
```
POST Authentication → Login (as provider)
POST Services → Create Service
```

### 3️⃣ Make Booking (1 min)
```
POST Authentication → Login (as customer)
POST Bookings → Create Booking
```

### 4️⃣ Process Booking (1 min)
```
POST Authentication → Login (as provider)
POST Bookings → Update Status - Confirm
POST Bookings → Update Status - In Progress
POST Bookings → Update Status - Completed
```

### 5️⃣ Leave Review (1 min)
```
POST Authentication → Login (as customer)
POST Reviews → Create Review
```

### 6️⃣ Respond (30 sec)
```
POST Authentication → Login (as provider)
POST Reviews → Respond to Review
```

✅ **Complete workflow tested in 5 minutes!**

---

## 🔐 Authentication

### Automatic Token Management

The collection automatically handles authentication:

**After Login:**
- ✅ `access_token` → Saved to environment
- ✅ `refresh_token` → Saved to environment
- ✅ `user_id` → Saved to environment

**All subsequent requests use:**
```
Authorization: Bearer {{access_token}}
```

**You never need to copy/paste tokens manually!** 🎉

---

## 🎯 Auto-Saved Variables

These variables are automatically set:

| Variable | Set After | Used In |
|----------|-----------|---------|
| `access_token` | Login | All authenticated endpoints |
| `refresh_token` | Login | Token refresh |
| `user_id` | Login | User-specific operations |
| `service_slug` | Create Service | Service operations |
| `booking_reference` | Create Booking | Booking operations |
| `provider_token` | Provider Registration | Quick provider login |
| `provider_id` | Provider Registration | Provider operations |

---

## 📝 Before First Test

### 1. Start Backend Server

**Docker:**
```bash
docker-compose up -d
```

**Local:**
```bash
python manage.py runserver
```

### 2. Create Service Category

Go to: http://localhost:8000/admin/

```
Add Service Category:
- Name: Plumbing
- Slug: plumbing
- Is Active: Yes
```

### 3. Run First Request

```
POST Authentication → Register Customer
```

✅ If you get `201 Created`, everything works!

---

## 🔄 Testing Different Users

### Switch Between Users:

**Test as Customer:**
```
1. POST Authentication → Login
2. Body: "email": "customer@example.com"
```

**Test as Provider:**
```
1. POST Authentication → Login
2. Body: "email": "provider@example.com"
```

Token automatically updates! 🔄

---

## 🛠️ Common Updates Needed

### 1. Service Category ID
In **Create Service** request:
```json
"category": 1  // ← Change to your category ID
```

### 2. Service ID
In **Create Booking** request:
```json
"service": 1  // ← Change to actual service ID
```

### 3. Booking Date
In **Create Booking** request:
```json
"scheduled_date": "2025-12-01"  // ← Use future date
```

### 4. Review Booking ID
In **Create Review** request:
```json
"booking": 1  // ← Use actual booking ID
```

---

## 🐛 Troubleshooting

### ❌ 401 Unauthorized
**Fix:** Re-login to get fresh token

### ❌ 404 Not Found
**Fix:** Check if server is running at `http://localhost:8000`

### ❌ 400 Bad Request
**Fix:** Update IDs in request body (category, service, booking)

### ❌ Variables not auto-saving
**Fix:** 
1. Check environment is selected (top right dropdown)
2. Response must be successful (200/201)

### ❌ Can't create booking
**Fix:**
1. Login as CUSTOMER (not provider)
2. Use valid service ID
3. Use future date

### ❌ Can't leave review
**Fix:**
1. Booking must be COMPLETED
2. Login as customer who made the booking
3. Can only review once per booking

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `Service Marketplace - Postman Collection` | The actual JSON collection |
| `POSTMAN_SETUP_GUIDE.md` | Detailed setup instructions |
| `POSTMAN_WALKTHROUGH.md` | Step-by-step tutorial (10 min) |
| `POSTMAN_COLLECTION_README.md` | This file - Quick reference |

---

## 🎓 Learning Path

### Beginner (Day 1):
1. Import collection
2. Follow "5-Minute Quick Test"
3. Test each endpoint individually

### Intermediate (Day 2):
1. Test all endpoints in each folder
2. Try different filters and searches
3. Test error scenarios

### Advanced (Day 3):
1. Use Collection Runner for automation
2. Add custom test scripts
3. Create monitoring workflows

---

## 💡 Pro Tips

### 1. Use Collection Runner
Test entire flow automatically:
```
Collection → Run → Select requests → Run
```

### 2. View Console
Debug requests:
```
View → Show Postman Console
```

### 3. Save Examples
Save successful responses:
```
Response → Save as Example
```

### 4. Environment for Production
Create separate environment:
```
base_url: https://api.yourdomain.com
```

### 5. Share with Team
```
Collection → Export → Share JSON file
```

---

## ✅ Success Indicators

After import, you should see:

- ✅ 50+ requests organized in folders
- ✅ Environment with `base_url` variable
- ✅ Bearer token auth configured
- ✅ Sample request bodies filled
- ✅ Test scripts for auto-saving variables

**Try the first request:**
```
POST Authentication → Register Customer
```

If you get `201 Created` → **Everything works!** 🎉

---

## 🚀 What You Can Test

### User Management
- ✅ Registration (4 roles)
- ✅ Login/Logout
- ✅ Profile updates
- ✅ Password management

### Service Management
- ✅ Browse/Search services
- ✅ Create/Update services (Provider)
- ✅ Service categories
- ✅ Service availability

### Booking System
- ✅ Create bookings (Customer)
- ✅ Status management (Provider)
- ✅ Cancellations
- ✅ Booking history

### Review System
- ✅ Leave reviews (Customer)
- ✅ Respond to reviews (Provider)
- ✅ Rating statistics
- ✅ Helpful votes

---

## 📊 API Coverage

- **Total Endpoints**: 50+
- **Authentication**: JWT Bearer token
- **Response Format**: JSON
- **Rate Limiting**: 1000 req/hour (authenticated)
- **Pagination**: 20 items/page (configurable)

---

## 🎯 Next Steps

### After Testing Collection:

1. **Frontend Integration**
   - Use same endpoints in React app
   - Copy request patterns

2. **Load Testing**
   - Use Newman CLI
   - Run automated tests

3. **CI/CD Integration**
   - Add to GitHub Actions
   - Automated testing on deploy

4. **Documentation**
   - Export as HTML
   - Share with team

---

## 🆘 Need Help?

### Resources:
- 📖 Full API Docs: `API_DOCUMENTATION.md`
- 🎬 Video Walkthrough: `POSTMAN_WALKTHROUGH.md`
- ⚙️ Setup Guide: `POSTMAN_SETUP_GUIDE.md`
- 🔧 Backend README: `README.md`

### Common Issues:
- Server not running → `python manage.py runserver`
- No category → Create in Django admin
- Wrong IDs → Check "List" endpoints for actual IDs
- Token expired → Re-login

---

## 🎊 You're All Set!

**Everything you need to test the Service Marketplace API is ready.**

**Import → Setup Environment → Start Testing!**

**Time to build something amazing! 🚀**