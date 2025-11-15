"""
Tests for Email OTP System
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import User, EmailOTP
from core.email_utils import EmailService


class EmailOTPModelTestCase(TestCase):
    """Test EmailOTP model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='+1234567890'
        )
    
    def test_create_otp(self):
        """Test creating an OTP"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        self.assertEqual(otp.otp_code, '123456')
        self.assertEqual(otp.purpose, 'EMAIL_VERIFICATION')
        self.assertFalse(otp.is_used)
        self.assertFalse(otp.is_expired)
        self.assertEqual(otp.attempts, 0)
    
    def test_otp_is_valid(self):
        """Test OTP validation"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        self.assertTrue(otp.is_valid())
    
    def test_otp_expired(self):
        """Test expired OTP"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        self.assertFalse(otp.is_valid())
    
    def test_otp_verify_success(self):
        """Test successful OTP verification"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        result = otp.verify('123456')
        self.assertTrue(result)
        self.assertTrue(otp.is_used)
        self.assertIsNotNone(otp.verified_at)
    
    def test_otp_verify_wrong_code(self):
        """Test OTP verification with wrong code"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        result = otp.verify('654321')
        self.assertFalse(result)
        self.assertFalse(otp.is_used)
        self.assertEqual(otp.attempts, 1)
    
    def test_otp_max_attempts(self):
        """Test OTP max attempts"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # Try wrong code 5 times
        for i in range(5):
            otp.verify('wrong')
        
        # OTP should be expired due to max attempts
        self.assertFalse(otp.is_valid())
        self.assertTrue(otp.is_expired)


class EmailOTPAPITestCase(APITestCase):
    """Test Email OTP API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='+1234567890'
        )
    
    def get_auth_token(self):
        """Get authentication token"""
        response = self.client.post('/api/users/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        return response.data['tokens']['access']
    
    def test_send_verification_otp(self):
        """Test sending verification OTP"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.post('/api/users/verify/send-otp/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check OTP was created
        otp_exists = EmailOTP.objects.filter(
            user=self.user,
            purpose='EMAIL_VERIFICATION'
        ).exists()
        self.assertTrue(otp_exists)
    
    def test_verify_email_otp_success(self):
        """Test successful email verification"""
        # Create OTP
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.post('/api/users/verify/confirm-otp/', {
            'otp_code': '123456'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user is verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
    
    def test_verify_email_otp_wrong_code(self):
        """Test email verification with wrong code"""
        otp = EmailOTP.objects.create(
            user=self.user,
            email=self.user.email,
            otp_code='123456',
            purpose='EMAIL_VERIFICATION',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.post('/api/users/verify/confirm-otp/', {
            'otp_code': '654321'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_password_reset_with_otp(self):
        """Test password reset flow with OTP"""
        # Request password reset
        response = self.client.post('/api/users/password/reset/request/', {
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get the OTP
        otp = EmailOTP.objects.filter(
            user=self.user,
            purpose='PASSWORD_RESET'
        ).latest('created_at')
        
        # Confirm password reset
        response = self.client.post('/api/users/password/reset/confirm/', {
            'email': 'test@example.com',
            'otp_code': otp.otp_code,
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Try logging in with new password
        response = self.client.post('/api/users/login/', {
            'email': 'test@example.com',
            'password': 'NewPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EmailServiceTestCase(TestCase):
    """Test Email Service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='+1234567890'
        )
    
    def test_send_otp_email(self):
        """Test sending OTP email"""
        result = EmailService.send_otp_email(
            self.user,
            '123456',
            'EMAIL_VERIFICATION'
        )
        # With console backend, this should return True
        self.assertTrue(result)
    
    def test_send_welcome_email(self):
        """Test sending welcome email"""
        result = EmailService.send_welcome_email(self.user)
        self.assertTrue(result)
    
    def test_send_verification_success_email(self):
        """Test sending verification success email"""
        result = EmailService.send_verification_success_email(self.user)
        self.assertTrue(result)
    
    def test_send_password_changed_email(self):
        """Test sending password changed email"""
        result = EmailService.send_password_changed_email(self.user)
        self.assertTrue(result)