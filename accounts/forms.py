from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class BaseRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=32, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone_number", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.role
        user.is_approved = self.role not in (User.Role.PATIENT, User.Role.DOCTOR, User.Role.DEPARTMENT)
        if commit:
            user.save()
        return user


class PatientRegistrationForm(BaseRegistrationForm):
    role = User.Role.PATIENT
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    device_id = forms.CharField(max_length=64, required=False, help_text="Wearable device serial number, if issued.")


class DoctorRegistrationForm(BaseRegistrationForm):
    role = User.Role.DOCTOR
    specialty = forms.CharField(max_length=120)
    license_number = forms.CharField(max_length=64)


class DepartmentRegistrationForm(BaseRegistrationForm):
    role = User.Role.DEPARTMENT
    department_name = forms.CharField(max_length=120)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
