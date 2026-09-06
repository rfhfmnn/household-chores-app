from django.contrib import admin
from .models import Household, UserProfile


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
