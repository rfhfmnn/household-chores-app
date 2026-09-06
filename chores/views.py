from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, HouseholdSelectionForm
from .models import Household, UserProfile


def household_required(view_func):
    """Decorator to ensure the authenticated user has selected a household."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.household:
            messages.warning(request, "Please select or create a household before accessing chores.")
            return redirect('household_select')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account was created successfully.")
            return redirect('household_select')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def household_select_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = HouseholdSelectionForm(request.POST)
        if form.is_valid():
            existing = form.cleaned_data.get('existing_household')
            new_name = form.cleaned_data.get('new_household_name')

            if existing:
                household = existing
                messages.success(request, f"You joined '{household.name}'!")
            else:
                household = Household.objects.create(name=new_name.strip())
                messages.success(request, f"Created and joined '{household.name}'!")

            profile.household = household
            profile.save()
            return redirect('dashboard')
    else:
        initial = {}
        if profile.household:
            initial['existing_household'] = profile.household
        form = HouseholdSelectionForm(initial=initial)

    return render(request, 'households/select_household.html', {'form': form})


@login_required
@household_required
def dashboard_view(request):
    household = request.user.profile.household
    members = household.members.select_related('user').all()
    return render(request, 'dashboard/dashboard.html', {
        'household': household,
        'household_members': members,
        'household_members_count': members.count(),
    })
