from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Household


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class HouseholdSelectionForm(forms.Form):
    existing_household = forms.ModelChoiceField(
        queryset=Household.objects.all(),
        required=False,
        empty_label="-- Select an existing household --",
        help_text="Choose a household that your roommates already created."
    )
    new_household_name = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Apartment 4B, Maple House'}),
        help_text="Or start a brand new household group."
    )

    def clean(self):
        cleaned_data = super().clean()
        existing = cleaned_data.get('existing_household')
        new_name = cleaned_data.get('new_household_name')

        if not existing and not (new_name and new_name.strip()):
            raise forms.ValidationError("Please select an existing household or enter a name to create a new one.")

        if existing and new_name and new_name.strip():
            raise forms.ValidationError("Please choose either an existing household or create a new one, not both.")

        return cleaned_data
