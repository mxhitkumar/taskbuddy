# Migration Guide: SMS OTP → Email OTP

## 🔄 What Changed

### Old System (SMS/Phone)
- ❌ Mixed email and phone OTP
- ❌ SMS costs
- ❌ Complex phone number validation
- ❌ International SMS issues
- ❌ Plain text notifications

### New System (Email Only)
- ✅ Email OTP only
- ✅ Zero cost (except SMTP)
- ✅ Professional HTML templates
- ✅ Works globally
- ✅ Rich formatting & branding

---

## 📋 Changes Checklist

### 1. Models Changed

**Old:** `OTPVerification`
```python
class OTPVerification(models.Model):
    user = models.ForeignKey(User)
    otp_type = CharField(choices=['EMAIL', 'PHONE', 'PASSWORD_RESET'])
    otp_code = CharField(max_length=6)
    is_used = BooleanField()
    expires_at = DateTimeField()
```

**New:** `EmailOTP`
```python
class EmailOTP(models.Model):
    user = models.ForeignKey(User)
    email = EmailField()  # NEW
    otp_code = CharField(max_length=6)
    purpose = CharField(choices=[
        'EMAIL_VERIFICATION',
        'PASSWORD_RESET',
        'LOGIN_2FA'
    ])
    
    # Enhanced security
    is_used = BooleanField()
    is_expired = BooleanField()  # NEW
    attempts = PositiveIntegerField()  # NEW
    max_attempts = PositiveIntegerField()  # NEW
    
    # Audit trail
    ip_address = GenericIPAddressField()  # NEW
    user_agent = TextField()  # NEW
    verified_at = DateTimeField()  # NEW
```

### 2. User Model Changed

**Old:**
```python
is_verified = BooleanField(default=False)  # Generic
```

**New:**
```python
is_email_verified = BooleanField(default=False)  # Specific
email_verified_at = DateTimeField(null=True)  # Timestamp
```

### 3. API Endpoints Changed

| Old Endpoint | New Endpoint | Change |
|--------------|--------------|--------|
| `/verify/send-otp/` | `/verify/send-otp/` | ✅ Same URL |
| Body: `{"otp_type": "EMAIL"}` | No body needed | 📝 Simplified |
| `/verify/confirm-otp/` | `/verify/confirm-otp/` | ✅ Same URL |
| Body: `{"otp_code": "...", "otp_type": "EMAIL", "email": "..."}` | Body: `{"otp_code": "..."}` | 📝 Simplified |

---

## 🚀 Migration Steps

### Step 1: Update Database

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

**Migration will:**
- Create `EmailOTP` table
- Add `is_email_verified` field to User
- Add `email_verified_at` field to User
- Keep old `OTPVerification` for reference (can be deleted later)

### Step 2: Update Environment Variables

```bash
# Add to .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Service Marketplace <noreply@marketplace.com>
```

### Step 3: Test Email Configuration

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'If you receive this, email is configured correctly!',
    'noreply@marketplace.com',
    ['your-email@example.com'],
    fail_silently=False,
)
```

### Step 4: Update Frontend (if applicable)

**Old API Call:**
```javascript
// Send OTP
POST /api/users/verify/send-otp/
{
  "otp_type": "EMAIL"  // ❌ Remove this
}

// Verify OTP
POST /api/users/verify/confirm-otp/
{
  "email": "user@example.com",  // ❌ Remove this
  "otp_code": "123456",
  "otp_type": "EMAIL"  // ❌ Remove this
}
```

**New API Call:**
```javascript
// Send OTP
POST /api/users/verify/send-otp/
// ✅ No body needed - uses authenticated user

// Verify OTP
POST /api/users/verify/confirm-otp/
{
  "otp_code": "123456"  // ✅ Only OTP code needed
}
```

### Step 5: Data Migration (Optional)

If you want to migrate existing verification status:

```python
# In Django shell
from users.models import User

# Mark all previously verified users
User.objects.filter(is_verified=True).update(
    is_email_verified=True,
    email_verified_at=timezone.now()
)
```

---

## 🔍 Testing Checklist

### 1. User Registration
- [ ] User receives welcome email
- [ ] User receives OTP email
- [ ] OTP email has correct format
- [ ] OTP is 6 digits
- [ ] OTP expires in 10 minutes

### 2. Email Verification
- [ ] Can request OTP
- [ ] OTP sent to correct email
- [ ] Can verify with correct OTP
- [ ] Invalid OTP shows error
- [ ] Expired OTP shows error
- [ ] Rate limiting works (3/hour)
- [ ] Attempts tracked correctly

### 3. Password Reset
- [ ] Can request reset OTP
- [ ] OTP sent to email
- [ ] Can reset with valid OTP
- [ ] Invalid OTP rejected
- [ ] Old OTPs invalidated after use

### 4. Email Templates
- [ ] Welcome email looks good
- [ ] OTP email formatted correctly
- [ ] Verification success email sent
- [ ] Password changed email sent
- [ ] All links work
- [ ] Branding correct

---

## 📊 Comparison

### Before (SMS + Email)
```python
# Complex OTP type handling
if otp_type == 'EMAIL':
    # Send email OTP
elif otp_type == 'PHONE':
    # Send SMS OTP (requires Twilio/etc)
    # Costs money per SMS
    # Phone number validation complex
```

### After (Email Only)
```python
# Simple, unified approach
EmailService.send_otp_email(user, otp_code, purpose)
# Always uses email
# No additional costs
# Works globally
```

---

## 💰 Cost Savings

### Old System (with SMS)
- Twilio: $0.0075 per SMS
- 10,000 users = $75/month
- International: $0.05 - $0.20 per SMS
- Phone number verification required

### New System (Email Only)
- Gmail: Free (limited)
- SendGrid: Free for 100/day, then $15/month for 40k
- AWS SES: $0.10 per 1,000 emails
- 10,000 users = $1/month (AWS SES)
- **Savings: 99%+**

---

## 🎯 Benefits Summary

### Security
- ✅ Attempt limiting (5 max)
- ✅ Rate limiting (3/hour)
- ✅ IP tracking
- ✅ Automatic expiration
- ✅ Audit trail

### User Experience
- ✅ Professional email design
- ✅ Clear instructions
- ✅ Branded templates
- ✅ Works on all devices
- ✅ No SMS delays

### Developer Experience
- ✅ Simpler code
- ✅ Easier testing
- ✅ Better error handling
- ✅ Comprehensive logs
- ✅ No external SMS service

### Operations
- ✅ Lower costs
- ✅ Better deliverability
- ✅ Global reach
- ✅ No phone validation
- ✅ Email analytics

---

## 🐛 Common Issues & Solutions

### Issue: OTP not received

**Old System:**
- SMS not delivered
- Phone number incorrect
- Carrier blocked
- International issues

**New System:**
- Check spam folder
- Verify email configuration
- Check SMTP logs
- Test with console backend first

### Issue: User can't verify

**Old System:**
- Multiple OTP types confusing
- Phone vs email unclear

**New System:**
- Single flow: email only
- Clear error messages
- Remaining attempts shown

---

## 📱 Mobile App Considerations

If you have a mobile app:

### Email Link Option
Consider adding "magic link" as alternative:

```python
# Generate secure token
token = signing.dumps(user.id, salt='email-verify')
verify_url = f"{BASE_URL}/verify/{token}"

# Send email with link instead of OTP
EmailService.send_verification_link(user, verify_url)
```

### Advantages:
- One-click verification
- No OTP typing needed
- Better mobile UX

---

## 🔄 Rollback Plan

If you need to rollback:

1. Keep old `OTPVerification` table
2. Don't delete old code immediately
3. Run both systems parallel for 1 week
4. Monitor adoption
5. Gradually phase out SMS

```python
# Feature flag approach
if settings.USE_EMAIL_OTP:
    # New system
    EmailOTP.objects.create(...)
else:
    # Old system
    OTPVerification.objects.create(...)
```

---

## ✅ Post-Migration Checklist

- [ ] All tests passing
- [ ] Email templates customized
- [ ] SMTP configured correctly
- [ ] Rate limiting tested
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team trained
- [ ] Users notified
- [ ] Old SMS service cancelled
- [ ] Cost savings verified

---

## 📞 Support

Need help with migration?
- Check logs: `logs/django.log`
- Test emails: Use console backend first
- Review: `EMAIL_OTP_SYSTEM_GUIDE.md`

**Migration Complete! 🎉**

Your platform now uses a modern, professional email OTP system!