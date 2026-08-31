from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import DeviceReadingForm
from .models import PatientProfile


@role_required(User.Role.PATIENT)
def upload_reading(request):
    profile = request.user.patient_profile
    if request.method == "POST":
        form = DeviceReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.patient = profile
            reading.save()
            messages.success(request, "Reading uploaded.")
            return redirect("patients:my_readings")
    else:
        form = DeviceReadingForm()
    return render(request, "patients/upload_reading.html", {"form": form})


@role_required(User.Role.PATIENT)
def my_readings(request):
    profile = request.user.patient_profile
    readings = profile.readings.all()[:100]
    return render(request, "patients/my_readings.html", {"readings": readings, "profile": profile})


@role_required(User.Role.PATIENT)
def my_prescriptions(request):
    profile = request.user.patient_profile
    prescriptions = profile.prescriptions.select_related("doctor__user").all()
    return render(request, "patients/my_prescriptions.html", {"prescriptions": prescriptions})
