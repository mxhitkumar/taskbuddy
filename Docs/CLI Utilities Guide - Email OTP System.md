# CLI Utilities Guide - Email OTP System

## 🛠️ Management Commands

The Email OTP system includes powerful management commands for testing, monitoring, and maintenance.

---

## 📧 Test Email Configuration

### Command: `test_email`

Test your email configuration by sending actual test emails.

```bash
# Test all email templates
python manage.py test_email your-email@example.com

# Test only OTP email
python manage.py test_email your-email@example.com --type=otp

# Test only welcome email
python manage.py test_email your-email@example.com --type=welcome
```

**Output:**
```
📧 Testing Email Configuration
============================================================

⚙️  Current Email Settings:
  Backend: django.core.mail.backends.smtp.EmailBackend
  Host: smtp.gmail.com
  Port: 587
  TLS: True
  From: Service Marketplace <noreply@marketplace.com>

👤 Creating/Getting test user for your-email@example.com...
  ✓ Test user created

📨 Testing OTP Email...
  ✓ OTP email sent successfully

👋 Testing Welcome Email...
  ✓ Welcome email sent successfully

✅ Testing Verification Success Email...
  ✓ Verification success email sent

🔒 Testing Password Changed Email...
  ✓ Password changed email sent

============================================================
📊 Results: 4 succeeded, 0 failed

✅ All email tests passed!
📬 Check your inbox at your-email@example.com
```

**Use Cases:**
- ✅ Verify SMTP configuration
- ✅ Test email templates
- ✅ Check email deliverability
- ✅ Debug email issues

---

## 🧹 Clean Up OTPs

### Command: `clean_otps`

Clean up expired and old OTP records.

```bash
# Default: Delete OTPs older than 30 days
python manage.py clean_otps

# Delete OTPs older than 7 days
python manage.py clean_otps --days=7

# Dry run (see what would be deleted)
python manage.py clean_otps --dry-run
```

**Output:**
```
🧹 Starting OTP cleanup...
✓ Marked 45 OTPs as expired
✓ Deleted 120 OTPs older than 30 days

📊 OTP Statistics:
  Total OTPs: 234
  Active: 12
  Used: 180
  Expired: 42

📧 By Purpose:
  EMAIL_VERIFICATION: 150
  PASSWORD_RESET: 80
  LOGIN_2FA: 4

✅ Cleanup complete!
```

**Recommended Schedule:**
```bash
# Daily via cron
0 2 * * * cd /path/to/project && python manage.py clean_otps
```

---

## 📊 OTP Statistics

### Command: `otp_stats`

View detailed OTP statistics and monitoring data.

```bash
# Stats for last 7 days
python manage.py otp_stats

# Stats for last 30 days
python manage.py otp_stats --days=30

# Detailed breakdown with top users
python manage.py otp_stats --detailed
```

**Output:**
```
📊 Email OTP Statistics (Last 7 days)
============================================================

📈 Overall Statistics:
  Total OTPs Generated: 456
  Successfully Used: 389 (85.3%)
  Expired: 45
  Active: 22
  Average Attempts: 1.34

📧 By Purpose:
  EMAIL_VERIFICATION: 300 (260 used, 86.7% success)
  PASSWORD_RESET: 150 (125 used, 83.3% success)
  LOGIN_2FA: 6 (4 used, 66.7% success)

✉️ Email Verification:
  New Users: 320
  Verified: 275
  Verification Rate: 85.9%

🚨 Potential Issues:
  No suspicious activity detected

🕐 Last 24 Hours:
  OTPs Generated: 68
  Successfully Verified: 58

✅ Statistics complete!
```

**With --detailed flag:**
```
👥 Top 10 Users by OTP Requests:
  1. user1@example.com: 5 OTPs
  2. user2@example.com: 4 OTPs
  3. user3@example.com: 3 OTPs

📅 Activity by Hour (Last 24h):
  09:00 - ████████ (8)
  10:00 - ██████████ (10)
  11:00 - ██████ (6)
  14:00 - ████████████ (12)
```

**Use Cases:**
- ✅ Monitor OTP usage
- ✅ Track success rates
- ✅ Identify issues
- ✅ Plan capacity

---

## 🧪 Running Tests

### Unit Tests

```bash
# Run all OTP tests
python manage.py test users.tests.test_email_otp

# Run specific test class
python manage.py test users.tests.test_email_otp.EmailOTPModelTestCase

# Run specific test
python manage.py test users.tests.test_email_otp.EmailOTPModelTestCase.test_otp_verify_success

# Run with coverage
pytest apps/users/tests/test_email_otp.py --cov=users
```

**Test Coverage:**
- ✅ EmailOTP model tests
- ✅ OTP verification logic
- ✅ API endpoint tests
- ✅ Email service tests
- ✅ Rate limiting tests

---

## 🔍 Database Inspection

### View OTPs in Database

```bash
python manage.py dbshell
```

```sql
-- View active OTPs
SELECT email, otp_code, purpose, attempts, expires_at 
FROM email_otps 
WHERE is_used = false AND is_expired = false 
ORDER BY created_at DESC 
LIMIT 10;

-- Success rate by purpose
SELECT 
    purpose,
    COUNT(*) as total,
    SUM(CASE WHEN is_used THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN is_used THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM email_otps
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY purpose;

-- Top users by OTP requests
SELECT 
    email,
    COUNT(*) as otp_count
FROM email_otps
GROUP BY email
ORDER BY otp_count DESC
LIMIT 10;
```

---

## 🐚 Django Shell Utilities

### Useful Shell Commands

```bash
python manage.py shell
```

#### 1. Check User Verification Status

```python
from users.models import User

# Get user
user = User.objects.get(email='user@example.com')

# Check status
print(f"Email Verified: {user.is_email_verified}")
print(f"Verified At: {user.email_verified_at}")
```

#### 2. Manually Verify User

```python
from django.utils import timezone

user.is_email_verified = True
user.email_verified_at = timezone.now()
user.save()
```

#### 3. Generate OTP Manually

```python
from users.models import EmailOTP
from datetime import timedelta
import random

otp_code = str(random.randint(100000, 999999))
otp = EmailOTP.objects.create(
    user=user,
    email=user.email,
    otp_code=otp_code,
    purpose='EMAIL_VERIFICATION',
    expires_at=timezone.now() + timedelta(minutes=10)
)
print(f"OTP: {otp_code}")
```

#### 4. Check OTP History

```python
from users.models import EmailOTP

# Recent OTPs for user
otps = EmailOTP.objects.filter(user=user).order_by('-created_at')[:5]

for otp in otps:
    print(f"{otp.purpose}: {otp.otp_code} - Used: {otp.is_used}")
```

#### 5. Test Email Sending

```python
from core.email_utils import EmailService

# Send test OTP
EmailService.send_otp_email(user, '123456', 'EMAIL_VERIFICATION')

# Send welcome email
EmailService.send_welcome_email(user)
```

#### 6. Calculate Statistics

```python
from django.db.models import Count, Avg
from datetime import timedelta

# Last 7 days
cutoff = timezone.now() - timedelta(days=7)
recent = EmailOTP.objects.filter(created_at__gte=cutoff)

stats = recent.aggregate(
    total=Count('id'),
    used=Count('id', filter=Q(is_used=True)),
    avg_attempts=Avg('attempts')
)

print(f"Total: {stats['total']}")
print(f"Used: {stats['used']}")
print(f"Success Rate: {stats['used']/stats['total']*100:.1f}%")
print(f"Avg Attempts: {stats['avg_attempts']:.2f}")
```

---

## 📋 Quick Reference

### Daily Operations

```bash
# Morning routine
python manage.py otp_stats --days=1        # Check yesterday's stats
python manage.py clean_otps --dry-run      # Preview cleanup

# Weekly maintenance
python manage.py otp_stats --days=7 --detailed
python manage.py clean_otps --days=7

# Test before changes
python manage.py test_email admin@example.com
python manage.py test users.tests.test_email_otp
```

### Troubleshooting

```bash
# Check email config
python manage.py test_email test@example.com --type=otp

# View recent activity
python manage.py otp_stats --days=1 --detailed

# Check for issues
python manage.py otp_stats | grep "suspicious"

# Clear old data
python manage.py clean_otps --days=1 --dry-run
python manage.py clean_otps --days=1
```

### Monitoring

```bash
# Hourly check (add to cron)
*/60 * * * * python manage.py otp_stats --days=1 >> /var/log/otp_stats.log

# Daily cleanup
0 2 * * * python manage.py clean_otps

# Weekly report
0 9 * * 1 python manage.py otp_stats --days=7 --detailed | mail -s "Weekly OTP Report" admin@example.com
```

---

## 🎯 Use Cases

### 1. New Deployment
```bash
# Test email configuration
python manage.py test_email admin@example.com

# Verify all templates work
python manage.py test_email admin@example.com --type=all

# Check initial stats
python manage.py otp_stats
```

### 2. Production Monitoring
```bash
# Daily health check
python manage.py otp_stats --days=1

# Weekly analysis
python manage.py otp_stats --days=7 --detailed

# Monthly cleanup
python manage.py clean_otps --days=30
```

### 3. Debugging Issues
```bash
# Check email sending
python manage.py test_email problematic-user@example.com

# View user's OTP history (in shell)
python manage.py shell
>>> from users.models import EmailOTP, User
>>> user = User.objects.get(email='problematic-user@example.com')
>>> EmailOTP.objects.filter(user=user).order_by('-created_at')

# Check for rate limiting
python manage.py otp_stats --detailed
```

---

## 💡 Pro Tips

### 1. Automate with Cron

Create `/etc/cron.d/marketplace-otp`:
```bash
# Clean old OTPs daily at 2 AM
0 2 * * * www-data cd /var/www/marketplace && python manage.py clean_otps

# Weekly stats email
0 9 * * 1 www-data cd /var/www/marketplace && python manage.py otp_stats --days=7 --detailed | mail -s "OTP Stats" admin@example.com
```

### 2. Add to CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Test Email System
  run: |
    python manage.py test users.tests.test_email_otp
    python manage.py test_email test@example.com
```

### 3. Health Check Script

```bash
#!/bin/bash
# check_otp_health.sh

# Run stats
stats=$(python manage.py otp_stats --days=1)

# Check success rate
success_rate=$(echo "$stats" | grep "Successfully Used" | awk '{print $4}' | tr -d '(%)' )

# Alert if below 80%
if (( $(echo "$success_rate < 80" | bc -l) )); then
    echo "OTP success rate below 80%: $success_rate%" | mail -s "OTP Alert" admin@example.com
fi
```

---

## 📞 Support Commands

### Get Help

```bash
# Command help
python manage.py test_email --help
python manage.py clean_otps --help
python manage.py otp_stats --help

# Django help
python manage.py help
```

### Check Installation

```bash
# Verify commands are available
python manage.py | grep -E "(test_email|clean_otps|otp_stats)"
```

---

**All CLI utilities are production-ready! 🚀**

Use these commands to monitor, test, and maintain your Email OTP system effectively.