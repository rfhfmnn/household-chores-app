from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class Household(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    household = models.ForeignKey(
        Household,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Chore(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='chores')
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    frequency_days = models.PositiveIntegerField(
        default=7,
        validators=[MinValueValidator(1)],
        help_text="Recurrence cadence in days (e.g. 1 for daily, 7 for weekly)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.household.name})"

    def create_initial_cycle(self):
        """Spawns cycle #1 in BIDDING status."""
        return ChoreCycle.objects.create(
            chore=self,
            cycle_number=1,
            due_date=timezone.now() + timedelta(days=self.frequency_days),
            status=ChoreCycle.Status.BIDDING,
        )

    def create_next_cycle(self):
        """Spawns the next sequential cycle in BIDDING status."""
        last_cycle = self.cycles.order_by('-cycle_number').first()
        next_num = (last_cycle.cycle_number + 1) if last_cycle else 1
        return ChoreCycle.objects.create(
            chore=self,
            cycle_number=next_num,
            due_date=timezone.now() + timedelta(days=self.frequency_days),
            status=ChoreCycle.Status.BIDDING,
        )


class ChoreCycle(models.Model):
    class Status(models.TextChoices):
        BIDDING = 'BIDDING', 'Bidding Open'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        COMPLETED = 'COMPLETED', 'Completed'

    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name='cycles')
    cycle_number = models.PositiveIntegerField(default=1)
    due_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BIDDING
    )
    assigned_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_cycles'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='completed_cycles'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date', 'cycle_number']
        constraints = [
            models.UniqueConstraint(
                fields=['chore', 'cycle_number'],
                name='unique_chore_cycle_number'
            )
        ]

    def __str__(self):
        return f"{self.chore.title} - Cycle #{self.cycle_number} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        """Returns True only when the task is ASSIGNED and currently past its due date."""
        return self.status == self.Status.ASSIGNED and timezone.now() > self.due_date


class Bid(models.Model):
    cycle = models.ForeignKey(ChoreCycle, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    preference_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Preference score from 1 (lowest) to 5 (highest)"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['cycle', 'user'],
                name='unique_cycle_user_bid'
            )
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.cycle} with {self.preference_score}"
