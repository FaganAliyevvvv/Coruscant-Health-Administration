from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from patients.models import PatientProfile

from .forms import PrescriptionForm, ServiceOrderForm
from .models import Prescription


@role_required(User.Role.DOCTOR)
def patient_list(request):
    patients = PatientProfile.objects.select_related("user").all()
    return render(request, "doctors/patient_list.html", {"patients": patients})


@role_required(User.Role.DOCTOR)
def patient_detail(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    readings = patient.readings.all()[:50]
    prescriptions = patient.prescriptions.select_related("doctor__user").all()
    orders = patient.service_orders.all()
    return render(
        request,
        "doctors/patient_detail.html",
        {"patient": patient, "readings": readings, "prescriptions": prescriptions, "orders": orders},
    )


@role_required(User.Role.DOCTOR)
def write_prescription(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user.doctor_profile
            prescription.patient = patient
            prescription.save()
            messages.success(request, "Prescription/report saved.")
            return redirect("doctors:patient_detail", patient_id=patient.id)
    else:
        form = PrescriptionForm()
    return render(request, "doctors/write_prescription.html", {"form": form, "patient": patient})


@role_required(User.Role.DOCTOR)
def create_order(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if request.method == "POST":
        form = ServiceOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.doctor = request.user.doctor_profile
            order.patient = patient
            order.save()
            messages.success(request, f"Order for {order.get_order_type_display()} created.")
            return redirect("doctors:patient_detail", patient_id=patient.id)
    else:
        form = ServiceOrderForm()
    return render(request, "doctors/create_order.html", {"form": form, "patient": patient})
