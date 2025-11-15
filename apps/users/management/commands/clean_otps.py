"""
Management command to clean up expired and old OTPs
Usage: python manage.py clean_otps
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.users.models import EmailOTP


class Command(BaseCommand):
    help = 'Clean up expired and old email OTPs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete OTPs older than N days (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('🧹 Starting OTP cleanup...'))
        
        # Mark expired OTPs
        expired_time = timezone.now()
        expired_otps = EmailOTP.objects.filter(
            expires_at__lt=expired_time,
            is_used=False,
            is_expired=False
        )
        
        expired_count = expired_otps.count()
        if not dry_run:
            expired_otps.update(is_expired=True)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Marked {expired_count} OTPs as expired')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would mark {expired_count} OTPs as expired')
            )
        
        # Delete old OTPs
        cutoff_date = timezone.now() - timedelta(days=days)
        old_otps = EmailOTP.objects.filter(created_at__lt=cutoff_date)
        
        old_count = old_otps.count()
        if not dry_run:
            old_otps.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Deleted {old_count} OTPs older than {days} days')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would delete {old_count} OTPs older than {days} days')
            )
        
        # Show statistics
        self.stdout.write('\n📊 OTP Statistics:')
        
        total = EmailOTP.objects.count()
        active = EmailOTP.objects.filter(
            is_used=False,
            is_expired=False,
            expires_at__gte=timezone.now()
        ).count()
        used = EmailOTP.objects.filter(is_used=True).count()
        expired = EmailOTP.objects.filter(is_expired=True).count()
        
        self.stdout.write(f'  Total OTPs: {total}')
        self.stdout.write(f'  Active: {active}')
        self.stdout.write(f'  Used: {used}')
        self.stdout.write(f'  Expired: {expired}')
        
        # Purpose breakdown
        self.stdout.write('\n📧 By Purpose:')
        for purpose in ['EMAIL_VERIFICATION', 'PASSWORD_RESET', 'LOGIN_2FA']:
            count = EmailOTP.objects.filter(purpose=purpose).count()
            self.stdout.write(f'  {purpose}: {count}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Cleanup complete!'))