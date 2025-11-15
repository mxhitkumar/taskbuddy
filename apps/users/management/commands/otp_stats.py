"""
Management command to view OTP statistics and monitoring
Usage: python manage.py otp_stats
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
from apps.users.models import EmailOTP, User


class Command(BaseCommand):
    help = 'Display email OTP statistics and monitoring data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Show stats for last N days (default: 7)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed breakdown'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        detailed = options['detailed']
        
        self.stdout.write(self.style.SUCCESS(f'📊 Email OTP Statistics (Last {days} days)'))
        self.stdout.write('=' * 60)
        
        # Date range
        cutoff_date = timezone.now() - timedelta(days=days)
        recent_otps = EmailOTP.objects.filter(created_at__gte=cutoff_date)
        
        # Overall Statistics
        self.stdout.write('\n📈 Overall Statistics:')
        total = recent_otps.count()
        used = recent_otps.filter(is_used=True).count()
        expired = recent_otps.filter(is_expired=True).count()
        active = recent_otps.filter(
            is_used=False,
            is_expired=False,
            expires_at__gte=timezone.now()
        ).count()
        
        success_rate = (used / total * 100) if total > 0 else 0
        
        self.stdout.write(f'  Total OTPs Generated: {total}')
        self.stdout.write(f'  Successfully Used: {used} ({success_rate:.1f}%)')
        self.stdout.write(f'  Expired: {expired}')
        self.stdout.write(f'  Active: {active}')
        
        # Average attempts
        avg_attempts = recent_otps.aggregate(Avg('attempts'))['attempts__avg'] or 0
        self.stdout.write(f'  Average Attempts: {avg_attempts:.2f}')
        
        # Purpose Breakdown
        self.stdout.write('\n📧 By Purpose:')
        purposes = recent_otps.values('purpose').annotate(
            count=Count('id'),
            used=Count('id', filter=Q(is_used=True))
        )
        
        for purpose in purposes:
            purpose_name = purpose['purpose']
            count = purpose['count']
            used_count = purpose['used']
            rate = (used_count / count * 100) if count > 0 else 0
            self.stdout.write(
                f'  {purpose_name}: {count} ({used_count} used, {rate:.1f}% success)'
            )
        
        # Verification Rate
        self.stdout.write('\n✉️ Email Verification:')
        total_users = User.objects.filter(created_at__gte=cutoff_date).count()
        verified_users = User.objects.filter(
            created_at__gte=cutoff_date,
            is_email_verified=True
        ).count()
        verification_rate = (verified_users / total_users * 100) if total_users > 0 else 0
        
        self.stdout.write(f'  New Users: {total_users}')
        self.stdout.write(f'  Verified: {verified_users}')
        self.stdout.write(f'  Verification Rate: {verification_rate:.1f}%')
        
        # Top Users by OTP Requests
        if detailed:
            self.stdout.write('\n👥 Top 10 Users by OTP Requests:')
            top_users = recent_otps.values(
                'user__email'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            for idx, user in enumerate(top_users, 1):
                self.stdout.write(f'  {idx}. {user["user__email"]}: {user["count"]} OTPs')
        
        # Failed Attempts
        failed = recent_otps.filter(
            is_used=False,
            is_expired=True,
            attempts__gte=3
        ).count()
        
        if failed > 0:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  {failed} OTPs failed after multiple attempts')
            )
        
        # Rate Limit Violations (high OTP requests)
        self.stdout.write('\n🚨 Potential Issues:')
        
        # Users with many OTP requests
        suspicious = recent_otps.values('user__email').annotate(
            count=Count('id')
        ).filter(count__gte=10)
        
        if suspicious.exists():
            self.stdout.write(
                self.style.ERROR(f'  {suspicious.count()} users with 10+ OTP requests')
            )
            if detailed:
                for user in suspicious[:5]:
                    self.stdout.write(f'    - {user["user__email"]}: {user["count"]} requests')
        else:
            self.stdout.write(self.style.SUCCESS('  No suspicious activity detected'))
        
        # Recent Activity (last 24 hours)
        self.stdout.write('\n🕐 Last 24 Hours:')
        last_24h = timezone.now() - timedelta(hours=24)
        recent = EmailOTP.objects.filter(created_at__gte=last_24h)
        
        self.stdout.write(f'  OTPs Generated: {recent.count()}')
        self.stdout.write(f'  Successfully Verified: {recent.filter(is_used=True).count()}')
        
        # Peak hours
        if detailed:
            self.stdout.write('\n📅 Activity by Hour (Last 24h):')
            for hour in range(24):
                hour_start = last_24h.replace(minute=0, second=0, microsecond=0) + timedelta(hours=hour)
                hour_end = hour_start + timedelta(hours=1)
                hour_count = EmailOTP.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end
                ).count()
                
                if hour_count > 0:
                    bar = '█' * (hour_count // 2 or 1)
                    self.stdout.write(f'  {hour:02d}:00 - {bar} ({hour_count})')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Statistics complete!'))