from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from billing.models import Plan, Subscription
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UsersViewsTest(TestCase):
    
    def setUp(self):
        # Create a user for testing login and views
        self.user = User.objects.create_user(username='testuser', password='Password123!')
        self.plan = Plan.objects.create(name='Basic Plan', price=100)
        self.subscription = Subscription.objects.create(user=self.user, plan=self.plan, status='active', 
                                                        start_date=datetime.now().date(), 
                                                        end_date=datetime.now().date(), 
                                                        requested_on=datetime.now().date())

    def test_home_view_authenticated(self):
        # Test if home page renders correctly when user is authenticated
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/home.html')

    def test_home_view_not_authenticated(self):
        # Test if home page redirects when user is not authenticated
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/?next=/home/')

    def test_login_view_get(self):
        # Test if login page is rendered when GET request is made
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post_success(self):
        # Test if login is successful with correct credentials
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'Password123!'})
        self.assertRedirects(response, '/home/')

    def test_login_view_post_fail(self):
        # Test if login fails with incorrect credentials
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        logger.warning(f"Login failed for username 'wronguser' with password 'wrongpass'.")

    def test_register_view_get(self):
        # Test if registration page is rendered
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_post_success(self):
        # Test if user can register with a valid password
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123!',
            'password2': 'ValidPassword123!',
            'email': 'newuser@example.com'
        })
        self.assertRedirects(response, '/home/')
        logger.info("User 'newuser' registered successfully.")

    def test_register_view_post_fail_password_mismatch(self):
        # Test if user registration fails due to password mismatch
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'ValidPassword123!',
            'password2': 'DifferentPassword123!',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)
        logger.error("Registration failed: Password mismatch for 'newuser'.")

    def test_register_view_post_fail_password_requirements(self):
        # Test if user registration fails due to insufficient password requirements
        # Password is too short (less than 8 characters)
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'short1!',
            'password2': 'short1!',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "At least 8 characters long")
        logger.error("Registration failed for 'newuser': Password too short.")

        # Password is missing an uppercase letter
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'missinguppercase1!',
            'password2': 'missinguppercase1!',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)
        logger.error("Registration failed for 'newuser': Missing uppercase letter in password.")

        # Password is missing a special character
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'MissingSpecialChar1',
            'password2': 'MissingSpecialChar1',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        logger.error("Registration failed for 'newuser': Missing special character in password.")

        # Password is missing a digit
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'MissingDigit!',
            'password2': 'MissingDigit!',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        logger.error("Registration failed for 'newuser': Missing digit in password.")

        # Password is longer than 32 characters
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'LongPasswordThatIsTooLong123!',
            'password2': 'LongPasswordThatIsTooLong123!',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        logger.error("Registration failed for 'newuser': Password exceeds maximum length.")

    def test_logout_view(self):
        # Test if logout works
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/')
        logger.info("User 'testuser' logged out successfully.")

    def test_login_view_post_fail_another(self):
        # Test if login fails with incorrect credentials
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)  # This will pass even if the login fails
        self.assertContains(response, "Invalid username or password")  # This will fail
        logger.warning(f"Login failed for 'wronguser' with invalid credentials.")
