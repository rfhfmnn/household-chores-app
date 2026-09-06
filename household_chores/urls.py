from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from chores import views as chore_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', chore_views.register_view, name='register'),

    # Household & Chores App
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('', include('chores.urls')),
]
