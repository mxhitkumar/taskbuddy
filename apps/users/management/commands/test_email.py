"""
Management command to test email configuration
Usage: python manage.py test_email your-email@example.com
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.email_utils import EmailService
from users.models import User


class Command(BaseCommand):
    help = 'Test email configuration by sending test emails'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['otp', 'welcome', 'all'],
            default='all',
            help='Type of email to test (default: all)'
        )
    
    def handle(self, *args, **options):
        email = options['email']
        test_type = options['type']
        
        self.stdout.write(self.style.SUCCESS(f'📧 Testing Email Configuration'))
        self.stdout.write('=' * 60)
        
        # Display current settings
        self.stdout.write('\n⚙️  Current Email Settings:')
        self.stdout.write(f'  Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'  Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'  TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  From: {settings.DEFAULT_FROM_EMAIL}')
        
        # Get or create test user
        self.stdout.write(f'\n👤 Creating/Getting test user for {email}...')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '+1234567890',
                'role': 'CUSTOMER'
            }
        )
        
        if created:
            user.set_password('TestPassword123!')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Test user created'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Using existing user'))
        
        # Test emails
        success_count = 0
        fail_count = 0
        
        if test_type in ['otp', 'all']:
            self.stdout.write('\n📨 Testing OTP Email...')
            try:
                result = EmailService.send_otp_email(user, '123456', 'EMAIL_VERIFICATION')
                if result:
                    self.stdout.write(self.style.SUCCESS('  ✓ OTP email sent successfully'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR('  ✗ Failed to send OTP email'))
                    fail_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                fail_count += 1
        
        if test_type in ['welcome', 'all']:
            self.stdout.write('\n👋 Testing Welcome Email...')
            try:
                result = EmailService.send_welcome_email(user)
                if result:
                    self.stdout.write(self.style.SUCCESS('  ✓ Welcome email sent successfully'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR('  ✗ Failed to send welcome email'))
                    fail_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                fail_count += 1
        
        if test_type == 'all':
            self.stdout.write('\n✅ Testing Verification Success Email...')
            try:
                result = EmailService.send_verification_success_email(user)
                if result:
                    self.stdout.write(self.style.SUCCESS('  ✓ Verification success email sent'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR('  ✗ Failed to send verification success email'))
                    fail_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                fail_count += 1
            
            self.stdout.write('\n🔒 Testing Password Changed Email...')
            try:
                result = EmailService.send_password_changed_email(user)
                if result:
                    self.stdout.write(self.style.SUCCESS('  ✓ Password changed email sent'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR('  ✗ Failed to send password changed email'))
                    fail_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                fail_count += 1
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(f'📊 Results: {success_count} succeeded, {fail_count} failed')
        
        if fail_count == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ All email tests passed!'))
            self.stdout.write(f'📬 Check your inbox at {email}')
            
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  Note: Using console backend. Emails printed above.'
                ))
        else:
            self.stdout.write(self.style.ERROR('\n❌ Some email tests failed!'))
            self.stdout.write('\n💡 Troubleshooting:')
            self.stdout.write('  1. Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env')
            self.stdout.write('  2. For Gmail, use App Password (not regular password)')
            self.stdout.write('  3. Check if port 587 is open (firewall)')
            self.stdout.write('  4. Try console backend for testing: EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend')