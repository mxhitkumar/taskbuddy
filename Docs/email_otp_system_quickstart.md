# Email OTP System - Quick Start (5 Minutes)

## 🚀 Get Running in 5 Minutes

### Step 1: Update Environment (1 minute)

Edit `.env`:
```bash
# For Gmail (Development)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=Service Marketplace <noreply@marketplace.com>
```

**Get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Generate password for "Mail"
3. Copy 16-character code

### Step 2: Run Migrations (1 minute)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Email Templates Directory (30 seconds)

```bash
mkdir -p templates/emails
```

### Step 4: Test Email Sending (30 seconds)

```bash
python manage.py shell
```

```python
from core.email_utils import EmailService
from users.models import User

# Get any user or create one
user = User.objects.first()

# Send test OTP
EmailService.send_otp_email(user, "123456", "EMAIL_VERIFICATION")
# Check your email!
```

### Step 5: Test API (2 minutes)

**Register User:**
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890",
    "role": "CUSTOMER"
  }'
```

**Check Your Email** → You'll receive:
1. Welcome email
2. OTP verification email (6-digit code)

**Verify Email:**
```bash
curl -X POST http://localhost:8000/api/users/verify/confirm-otp/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"otp_code": "123456"}'
```

✅ **Done! Email OTP is working!**

---

## 🧪 Quick Test Checklist

- [ ] Gmail App Password generated
- [ ] `.env` updated with email credentials
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Email templates directory created
- [ ] Test email sent successfully
- [ ] User registered and received emails
- [ ] OTP verification works
- [ ] Welcome email received
- [ ] Verification success email received

---

## 🐛 Troubleshooting

### Email Not Sending?

**1. Check Console First:**
```python
# In .env, temporarily use console backend
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails will print to console - good for testing!

**2. Test SMTP Connection:**
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test',
    'Testing SMTP',
    'noreply@example.com',
    ['your-email@example.com'],
    fail_silently=False
)
```

**3. Common Issues:**

| Issue | Solution |
|-------|----------|
| Authentication failed | Use App Password, not regular password |
| Connection refused | Check firewall, port 587 open |
| Invalid credentials | Double-check EMAIL_HOST_USER and PASSWORD |
| Emails in spam | Configure SPF/DKIM (production only) |

---

## 📧 Email Providers Quick Setup

### Gmail (Free - Development)
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Not regular password!
```

### SendGrid (Free Tier - Production)
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey  # Literally "apikey"
EMAIL_HOST_PASSWORD=SG.your-actual-api-key-here
```

### AWS SES (Pay-as-you-go)
```bash
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=your-ses-smtp-username
EMAIL_HOST_PASSWORD=your-ses-smtp-password
```

---

## 🎯 What You Get

### Email Templates
- ✅ OTP Verification (professional design)
- ✅ Welcome Email (personalized by role)
- ✅ Verification Success
- ✅ Password Changed Notification

### API Endpoints
- ✅ `/api/users/register/` - Auto-sends OTP
- ✅ `/api/users/verify/send-otp/` - Request OTP
- ✅ `/api/users/verify/confirm-otp/` - Verify OTP
- ✅ `/api/users/password/reset/request/` - Reset OTP
- ✅ `/api/users/password/reset/confirm/` - Confirm reset

### Security Features
- ✅ 6-digit OTP (100,000 - 999,999)
- ✅ 10-minute expiration
- ✅ Max 5 verification attempts
- ✅ Rate limiting (3 requests/hour)
- ✅ IP & user agent tracking
- ✅ Auto-expiration of old OTPs

---

## 📚 Full Documentation

- **Complete Guide**: `EMAIL_OTP_SYSTEM_GUIDE.md`
- **Migration Guide**: `OTP_MIGRATION_GUIDE.md`
- **Improvements**: `EMAIL_OTP_IMPROVEMENTS_SUMMARY.md`
- **API Docs**: `API_DOCUMENTATION.md`

---

## ✅ Success!

If you can:
1. Register a user
2. Receive welcome + OTP emails
3. Verify with OTP code
4. See "Email verified successfully"

**You're done! Email OTP system is working! 🎉**

---

## 🎨 Customization (Optional)

### Change OTP Expiration
```python
# In views.py, change timedelta
expires_at = timezone.now() + timedelta(minutes=15)  # 15 minutes instead of 10
```

### Customize Email Templates
```bash
# Edit templates/emails/*.html
# Add your logo, colors, branding
```

### Change Rate Limit
```python
# In settings/base.py
EMAIL_RATE_LIMIT_PER_HOUR = 5  # 5 instead of 3
```

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Switch to SendGrid/AWS SES
- [ ] Configure SPF/DKIM records
- [ ] Test email deliverability
- [ ] Customize email templates with branding
- [ ] Set up email monitoring
- [ ] Configure error alerting
- [ ] Test rate limiting
- [ ] Review security settings
- [ ] Update `DEFAULT_FROM_EMAIL`
- [ ] Test password reset flow

---

## 📞 Need Help?

**Quick Fixes:**
- Console backend not working? Check `EMAIL_BACKEND` in `.env`
- Emails not received? Check spam folder
- OTP invalid? Check server time/timezone
- Rate limit? Wait 1 hour or clear Redis

**Documentation:**
- Full setup: `EMAIL_OTP_SYSTEM_GUIDE.md`
- Migration: `OTP_MIGRATION_GUIDE.md`
- API reference: `API_DOCUMENTATION.md`

**Your Email OTP System is Ready! 📧🔐**