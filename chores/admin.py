from django.contrib import admin
from .models import Household, UserProfile, Chore, ChoreCycle, Bid


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'member_count')
    search_fields = ('name',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'household', 'created_at')
    list_filter = ('household',)
    search_fields = ('user__username', 'user__email', 'household__name')


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'household', 'frequency_days', 'is_active', 'created_at')
    list_filter = ('household', 'is_active')
    search_fields = ('title', 'household__name')


@admin.register(ChoreCycle)
class ChoreCycleAdmin(admin.ModelAdmin):
    list_display = ('chore', 'cycle_number', 'status', 'assigned_to', 'due_date', 'is_overdue_flag')
    list_filter = ('status', 'chore__household')
    search_fields = ('chore__title', 'assigned_to__username')

    def is_overdue_flag(self, obj):
        return obj.is_overdue
    is_overdue_flag.boolean = True
    is_overdue_flag.short_description = 'Overdue'


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('cycle', 'user', 'preference_score', 'submitted_at')
    list_filter = ('preference_score', 'cycle__chore__household')
    search_fields = ('user__username', 'cycle__chore__title')
