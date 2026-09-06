from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Household, UserProfile


class HouseholdAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='roommate1',
            password='Password123!',
            email='roommate1@example.com'
        )

    def test_user_profile_created_by_signal(self):
        """Test that UserProfile is automatically created on user creation via signal."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
        self.assertIsNone(self.user.profile.household)

    def test_dashboard_redirects_unauthenticated_user(self):
        """Test that unauthenticated user trying to access dashboard is redirected to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_redirects_user_without_household(self):
        """Test that logged-in user without household is redirected to household select."""
        self.client.login(username='roommate1', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('household_select'))

    def test_create_and_join_new_household(self):
        """Test creating a new household via the household selection view."""
        self.client.login(username='roommate1', password='Password123!')
        response = self.client.post(reverse('household_select'), {
            'new_household_name': 'Apartment 4B',
        })
        self.assertRedirects(response, reverse('dashboard'))

        self.user.profile.refresh_from_db()
        self.assertIsNotNone(self.user.profile.household)
        self.assertEqual(self.user.profile.household.name, 'Apartment 4B')
        self.assertIn(self.user.profile, self.user.profile.household.members.all())

    def test_join_existing_household(self):
        """Test joining an existing household created by another user."""
        household = Household.objects.create(name='Maple Street House')
        self.client.login(username='roommate1', password='Password123!')

        response = self.client.post(reverse('household_select'), {
            'existing_household': household.id,
        })
        self.assertRedirects(response, reverse('dashboard'))

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.household, household)

    def test_user_registration_view(self):
        """Test user registration endpoint creates user and logs them in."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
        })
        self.assertRedirects(response, reverse('household_select'))
        created_user = User.objects.get(username='newuser')
        self.assertEqual(created_user.email, 'newuser@example.com')
        self.assertTrue(hasattr(created_user, 'profile'))

    def test_authenticated_dashboard_view(self):
        """Test accessing dashboard after joining a household."""
        household = Household.objects.create(name='Maple Street House')
        self.user.profile.household = household
        self.user.profile.save()

        self.client.login(username='roommate1', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maple Street House')
        self.assertContains(response, 'roommate1')
