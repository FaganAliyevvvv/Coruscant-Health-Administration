from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from doctors.models import DoctorProfile
from patients.models import PatientProfile

from .forms import DepartmentRegistrationForm, DoctorRegistrationForm, PatientRegistrationForm
from .models import User


class CHALoginView(LoginView):
    template_name = "accounts/login.html"


class CHALogoutView(LogoutView):
    next_page = "core:home"


def register_patient(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                PatientProfile.objects.create(
                    user=user,
                    date_of_birth=form.cleaned_data["date_of_birth"],
                    device_id=form.cleaned_data.get("device_id", ""),
                )
            login(request, user)
            messages.success(
                request,
                "Registration received. An Administrator must approve your account before "
                "you can upload readings.",
            )
            return redirect("core:dashboard")
    else:
        form = PatientRegistrationForm()
    return render(request, "accounts/register.html", {"form": form, "role": "Patient"})


def register_doctor(request):
    if request.method == "POST":
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                DoctorProfile.objects.create(
                    user=user,
                    specialty=form.cleaned_data["specialty"],
                    license_number=form.cleaned_data["license_number"],
                )
            login(request, user)
            messages.success(
                request,
                "Registration received. An Administrator must approve your account before "
                "you can access patient records.",
            )
            return redirect("core:dashboard")
    else:
        form = DoctorRegistrationForm()
    return render(request, "accounts/register.html", {"form": form, "role": "Doctor"})


def register_department(request):
    if request.method == "POST":
        form = DepartmentRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user.first_name = user.first_name or form.cleaned_data["department_name"]
                user.save(update_fields=["first_name"])
            login(request, user)
            messages.success(request, "Registration received, pending Administrator approval.")
            return redirect("core:dashboard")
    else:
        form = DepartmentRegistrationForm()
    return render(request, "accounts/register.html", {"form": form, "role": "Department"})


def register_choice(request):
    return render(request, "accounts/register_choice.html")
