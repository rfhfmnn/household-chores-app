from django.urls import path
from . import views

urlpatterns = [
    path('household/select/', views.household_select_view, name='household_select'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
