# Postman Collection Setup Guide

## 📥 Import the Collection

### Method 1: Direct Import (Recommended)

1. **Copy the JSON content** from `Service Marketplace - Postman Collection` artifact
2. **Open Postman**
3. Click **Import** button (top left)
4. Select **Raw text** tab
5. **Paste** the entire JSON content
6. Click **Import**

### Method 2: Import from File

1. **Save the JSON** as `service-marketplace-api.postman_collection.json`
2. **Open Postman**
3. Click **Import** button
4. **Drag and drop** the file or click **Choose Files**
5. Click **Import**

---

## 🔧 Setup Environment Variables

### Create Environment

1. Click on **Environments** (left sidebar)
2. Click **+** to create new environment
3. Name it: `Service Marketplace - Local`
4. Add these variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `access_token` | ` ` | ` ` |
| `refresh_token` | ` ` | ` ` |
| `user_id` | ` ` | ` ` |
| `booking_reference` | ` ` | ` ` |
| `service_slug` | ` ` | ` ` |
| `provider_token` | ` ` | ` ` |
| `provider_id` | ` ` | ` ` |

5. Click **Save**
6. Select this environment from the dropdown (top right)

---

## 🚀 Quick Start - Test Complete Flow

### Step 1: Setup Data (Django Admin)

Before testing APIs, create initial data:

```bash
# Access Django admin
http://localhost:8000/admin/

# Create Service Category
Name: Plumbing
Slug: plumbing
Is Active: Yes
```

### Step 2: Test the API Flow

Follow this exact sequence for a complete test:

#### 1️⃣ **Register Customer** ✅
```
POST Authentication → Register Customer
```
- Auto-saves `access_token`, `refresh_token`, `user_id`
- Check: Response should be 201 Created

#### 2️⃣ **Register Service Provider** ✅
```
POST Authentication → Register Service Provider
```
- Auto-saves `provider_token`, `provider_id`
- Check: Response should be 201 Created

#### 3️⃣ **Login as Customer** ✅
```
POST Authentication → Login
Body: Change to customer@example.com
```
- Updates `access_token`
- Check: Response should be 200 OK

#### 4️⃣ **Get My Profile** ✅
```
GET User Profile → Get My Profile
```
- Check: Should return your profile data

#### 5️⃣ **Login as Provider** ✅
```
POST Authentication → Login
Body: Change email to provider@example.com
```
- Now you're logged in as provider

#### 6️⃣ **Create Service** ✅
```
POST Services → Create Service (Provider)
```
- Auto-saves `service_slug`
- Check: Response should be 201 Created
- Note: Update `category` ID if needed

#### 7️⃣ **List Services** ✅
```
GET Services → List Services
```
- Check: Should see your created service

#### 8️⃣ **Login as Customer Again** ✅
```
POST Authentication → Login
Body: customer@example.com
```
- Switch back to customer

#### 9️⃣ **Create Booking** ✅
```
POST Bookings → Create Booking
```
- Auto-saves `booking_reference`
- Update `service` ID in body
- Check: Response should be 201 Created

#### 🔟 **Get Booking Details** ✅
```
GET Bookings → Get Booking Details
```
- Check: Should show booking with PENDING status

#### 1️⃣1️⃣ **Login as Provider** ✅
```
POST Authentication → Login
Body: provider@example.com
```

#### 1️⃣2️⃣ **Confirm Booking** ✅
```
POST Bookings → Update Booking Status - Confirm
```
- Check: Status changes to CONFIRMED

#### 1️⃣3️⃣ **Start Work** ✅
```
POST Bookings → Update Booking Status - In Progress
```
- Check: Status changes to IN_PROGRESS

#### 1️⃣4️⃣ **Complete Work** ✅
```
POST Bookings → Update Booking Status - Completed
```
- Check: Status changes to COMPLETED

#### 1️⃣5️⃣ **Login as Customer** ✅
```
POST Authentication → Login
Body: customer@example.com
```

#### 1️⃣6️⃣ **Leave Review** ✅
```
POST Reviews → Create Review
```
- Update `booking` ID in body
- Check: Response should be 201 Created

#### 1️⃣7️⃣ **View Reviews** ✅
```
GET Reviews → List Reviews
```
- Check: Should see your review

#### 1️⃣8️⃣ **Login as Provider** ✅
```
POST Authentication → Login
Body: provider@example.com
```

#### 1️⃣9️⃣ **Respond to Review** ✅
```
POST Reviews → Respond to Review (Provider)
```
- Update review ID in URL (use 1 or check from previous response)
- Check: Response should be 201 Created

#### 2️⃣0️⃣ **View Review Statistics** ✅
```
GET Reviews → Review Statistics
```
- Check: Should show rating statistics

---

## 🎯 Auto-Generated Variables

The collection automatically saves these variables after certain requests:

### After Registration/Login:
- ✅ `access_token` - JWT access token (auto-set)
- ✅ `refresh_token` - JWT refresh token (auto-set)
- ✅ `user_id` - User ID (auto-set)

### After Creating Service:
- ✅ `service_slug` - Service slug (auto-set)

### After Creating Booking:
- ✅ `booking_reference` - Booking reference (auto-set)

**You don't need to copy/paste these manually!** 🎉

---

## 🔐 Authentication

### Bearer Token is Auto-Configured

The collection uses Bearer token authentication automatically:
- Header: `Authorization: Bearer {{access_token}}`
- Token is auto-set after login
- Works for all authenticated endpoints

### Endpoints Without Auth:
- ✅ Register
- ✅ Login
- ✅ List Categories
- ✅ List Services
- ✅ Service Details
- ✅ List Reviews
- ✅ Review Statistics

---

## 📝 Common Modifications

### Update IDs Before Testing:

1. **Service Category ID** (in Create Service)
   ```json
   "category": 1  // Change if needed
   ```

2. **Service ID** (in Create Booking)
   ```json
   "service": 1  // Use actual service ID
   ```

3. **Booking ID** (in Create Review)
   ```json
   "booking": 1  // Use actual booking ID
   ```

4. **Review ID** (in URL for Respond to Review)
   ```
   /api/reviews/1/respond/  // Change 1 to actual review ID
   ```

### Update Dates:

In **Create Booking**, make sure date is in future:
```json
"scheduled_date": "2025-11-15",  // Update to future date
"scheduled_time": "10:00:00"
```

---

## 🧪 Testing Different Scenarios

### Test as Customer:
```
1. Login → customer@example.com
2. Browse Services
3. Create Booking
4. View Bookings
5. Cancel Booking
6. Leave Review
```

### Test as Provider:
```
1. Login → provider@example.com
2. Create Service
3. View My Services
4. Confirm Bookings
5. Update Booking Status
6. Respond to Reviews
```

### Test as Admin:
```
1. Create admin user via: python manage.py createsuperuser
2. Login with admin credentials
3. Access all endpoints
4. Verify providers
```

---

## 🔄 Switching Users

### Quick Switch Method:

1. Go to **Authentication → Login**
2. Update `email` in body:
   - Customer: `customer@example.com`
   - Provider: `provider@example.com`
3. Send request
4. Token automatically updates

### Multiple Token Management:

Save different tokens for quick switching:
- Create separate environment for each user
- Or manually save tokens in environment variables:
  - `customer_token`
  - `provider_token`
  - `admin_token`

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized

**Solution:**
```
1. Check if access_token is set in environment
2. Re-login to get fresh token
3. Ensure environment is selected (top right)
```

### Issue: 404 Not Found

**Solution:**
```
1. Check if server is running: http://localhost:8000
2. Verify URL in environment variable
3. Check if endpoint exists in API
```

### Issue: 400 Bad Request

**Solution:**
```
1. Check request body format
2. Verify all required fields
3. Update IDs (category, service, booking)
4. Check date format (YYYY-MM-DD)
```

### Issue: 403 Forbidden

**Solution:**
```
1. Check user role permissions
2. Customer can't create services
3. Provider can't create bookings for others
4. Use correct account type
```

### Issue: Token Expired

**Solution:**
```
1. Go to Authentication → Refresh Token
2. Or re-login to get new tokens
```

### Issue: Variables Not Auto-Setting

**Solution:**
```
1. Check if environment is selected
2. Look at Tests tab in request
3. Response must be successful (200/201)
4. Manually set variables if needed
```

---

## 📊 Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed |
| 201 | Created | Resource created |
| 400 | Bad Request | Check request body |
| 401 | Unauthorized | Login again |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check URL/ID |
| 500 | Server Error | Check server logs |

---

## 🎨 Organizing Requests

### Folders in Collection:
```
📁 Authentication
  ├── Register Customer
  ├── Register Service Provider
  ├── Login
  └── Refresh Token

📁 User Profile
  ├── Get My Profile
  ├── Update Profile
  └── Change Password

📁 Service Categories
  └── List Categories

📁 Services
  ├── List Services
  ├── Search Services
  ├── Get Service Details
  ├── Create Service
  └── My Services

📁 Bookings
  ├── Create Booking
  ├── List Bookings
  ├── Update Status (Confirm, Start, Complete)
  └── Cancel Booking

📁 Reviews
  ├── Create Review
  ├── List Reviews
  ├── Respond to Review
  └── Review Statistics
```

---

## 💡 Pro Tips

### 1. Use Collection Runner
```
1. Click on collection name
2. Click "Run"
3. Select requests to run
4. Run entire flow automatically
```

### 2. Save Responses
```
Right-click on request → Save Response
Good for testing and debugging
```

### 3. Use Pre-request Scripts
```javascript
// Auto-generate dates
pm.environment.set("future_date", 
  new Date(Date.now() + 30*24*60*60*1000)
  .toISOString().split('T')[0]
);
```

### 4. Create Test Scripts
```javascript
// In Tests tab
pm.test("Status is 200", () => {
  pm.response.to.have.status(200);
});

pm.test("Has access token", () => {
  pm.expect(pm.response.json()).to.have.property('tokens');
});
```

### 5. Export Collection
```
Right-click collection → Export
Share with team members
```

---

## 🚀 Advanced Usage

### Environment for Production

Create second environment for production:

| Variable | Value |
|----------|-------|
| `base_url` | `https://api.yourdomain.com` |
| `access_token` | ` ` |
| `refresh_token` | ` ` |

### Automated Testing

```javascript
// Add to Collection Tests tab
pm.test("Response time is less than 200ms", () => {
  pm.expect(pm.response.responseTime).to.be.below(200);
});

pm.test("Response has correct structure", () => {
  const json = pm.response.json();
  pm.expect(json).to.have.property('results');
});
```

### Mock Server

1. Click on collection
2. Click "..."
3. Select "Mock Collection"
4. Use for frontend development without backend

---

## 📚 Additional Resources

- **Postman Documentation**: https://learning.postman.com/
- **API Documentation**: See `API_DOCUMENTATION.md`
- **Backend Setup**: See `README.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`

---

## ✅ Verification Checklist

After import, verify:

- [ ] Collection imported successfully
- [ ] Environment created and selected
- [ ] `base_url` points to your server
- [ ] Server is running (http://localhost:8000)
- [ ] Database migrations applied
- [ ] Service category created in admin
- [ ] Can register customer
- [ ] Can register provider
- [ ] Tokens auto-save after login
- [ ] Can create service as provider
- [ ] Can create booking as customer
- [ ] Can leave review after completion

---

## 🎉 You're All Set!

Your Postman collection is ready to use. Follow the **Quick Start - Test Complete Flow** section above to test the entire platform.

**Happy Testing! 🚀**