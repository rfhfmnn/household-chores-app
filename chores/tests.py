from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Household, UserProfile, Chore, ChoreCycle, Bid


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

    def test_register_duplicate_username_fails(self):
        """Test that registering an already existing username fails with a form error."""
        response = self.client.post(reverse('register'), {
            'username': 'roommate1',
            'email': 'different@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'A user with that username already exists.')

    def test_household_selection_validation_empty(self):
        """Test that submitting empty household selection form produces error."""
        self.client.login(username='roommate1', password='Password123!')
        response = self.client.post(reverse('household_select'), {
            'existing_household': '',
            'new_household_name': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_household_selection_validation_both_selected(self):
        """Test that selecting both existing and new household raises validation error."""
        h = Household.objects.create(name='Existing House')
        self.client.login(username='roommate1', password='Password123!')
        response = self.client.post(reverse('household_select'), {
            'existing_household': h.id,
            'new_household_name': 'Conflicting New House',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())

    def test_switch_household(self):
        """Test switching from one household to another."""
        h1 = Household.objects.create(name='House 1')
        h2 = Household.objects.create(name='House 2')
        self.user.profile.household = h1
        self.user.profile.save()

        self.client.login(username='roommate1', password='Password123!')
        response = self.client.post(reverse('household_select'), {
            'existing_household': h2.id,
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.household, h2)
        self.assertEqual(h1.members.count(), 0)
        self.assertEqual(h2.members.count(), 1)

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


class CoreChoreModelsTests(TestCase):
    def setUp(self):
        self.household = Household.objects.create(name='Sunny Apartment')
        self.user1 = User.objects.create_user(username='alice', password='Password123!')
        self.user2 = User.objects.create_user(username='bob', password='Password123!')
        self.user1.profile.household = self.household
        self.user1.profile.save()
        self.user2.profile.household = self.household
        self.user2.profile.save()

        self.chore = Chore.objects.create(
            household=self.household,
            title='Kitchen Dishes',
            description='Wash pots, pans and run dishwasher',
            frequency_days=2
        )

    def test_chore_creation_and_cycle_spawning(self):
        """Test initial and sequential cycle creation helpers on Chore model."""
        cycle1 = self.chore.create_initial_cycle()
        self.assertEqual(cycle1.cycle_number, 1)
        self.assertEqual(cycle1.status, ChoreCycle.Status.BIDDING)
        self.assertEqual(self.chore.cycles.count(), 1)
        self.assertGreater(cycle1.due_date, timezone.now())

        cycle2 = self.chore.create_next_cycle()
        self.assertEqual(cycle2.cycle_number, 2)
        self.assertEqual(cycle2.status, ChoreCycle.Status.BIDDING)
        self.assertEqual(self.chore.cycles.count(), 2)

    def test_chore_cycle_is_overdue_property(self):
        """Test is_overdue property under different statuses and dates."""
        now = timezone.now()

        # Assigned and past due date -> Overdue
        past_cycle = ChoreCycle.objects.create(
            chore=self.chore,
            cycle_number=1,
            due_date=now - timedelta(hours=5),
            status=ChoreCycle.Status.ASSIGNED,
            assigned_to=self.user1
        )
        self.assertTrue(past_cycle.is_overdue)

        # Assigned and future due date -> NOT overdue
        future_cycle = ChoreCycle.objects.create(
            chore=self.chore,
            cycle_number=2,
            due_date=now + timedelta(days=2),
            status=ChoreCycle.Status.ASSIGNED,
            assigned_to=self.user1
        )
        self.assertFalse(future_cycle.is_overdue)

        # Completed, even if past due date -> NOT overdue
        completed_cycle = ChoreCycle.objects.create(
            chore=self.chore,
            cycle_number=3,
            due_date=now - timedelta(days=1),
            status=ChoreCycle.Status.COMPLETED,
            assigned_to=self.user1,
            completed_at=now,
            completed_by=self.user1
        )
        self.assertFalse(completed_cycle.is_overdue)

        # In BIDDING status, even if past due date -> NOT overdue
        bidding_cycle = ChoreCycle.objects.create(
            chore=self.chore,
            cycle_number=4,
            due_date=now - timedelta(days=1),
            status=ChoreCycle.Status.BIDDING
        )
        self.assertFalse(bidding_cycle.is_overdue)

    def test_bid_unique_constraint(self):
        """Test that a user cannot place more than one bid on the same cycle."""
        cycle = self.chore.create_initial_cycle()

        Bid.objects.create(
            cycle=cycle,
            user=self.user1,
            preference_score=4
        )

        with self.assertRaises(IntegrityError):
            Bid.objects.create(
                cycle=cycle,
                user=self.user1,
                preference_score=2
            )

    def test_bid_preference_score_validation(self):
        """Test preference score validator (between 1 and 5)."""
        cycle = self.chore.create_initial_cycle()

        # Valid score 1 and 5
        valid_bid = Bid(cycle=cycle, user=self.user1, preference_score=5)
        valid_bid.full_clean()

        # Invalid score 0
        invalid_bid_low = Bid(cycle=cycle, user=self.user2, preference_score=0)
        with self.assertRaises(ValidationError):
            invalid_bid_low.full_clean()

        # Invalid score 6
        invalid_bid_high = Bid(cycle=cycle, user=self.user2, preference_score=6)
        with self.assertRaises(ValidationError):
            invalid_bid_high.full_clean()
