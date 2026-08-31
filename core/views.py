from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import User
from patients.models import PatientProfile


def home(request):
    if request.user.is_authenticated:
        return dashboard(request)
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    user = request.user
    context = {}
    if user.role == User.Role.ADMINISTRATOR:
        pending_users = User.objects.filter(is_approved=False)
        context["pending_users"] = pending_users
        context["total_patients"] = User.objects.filter(role=User.Role.PATIENT, is_approved=True).count()
        context["total_doctors"] = User.objects.filter(role=User.Role.DOCTOR, is_approved=True).count()
        from orders.models import ServiceOrder

        context["open_orders"] = ServiceOrder.objects.exclude(
            status__in=[ServiceOrder.Status.COMPLETED, ServiceOrder.Status.CANCELLED]
        ).count()
    elif user.role == User.Role.PATIENT and hasattr(user, "patient_profile"):
        context["profile"] = user.patient_profile
        context["recent_readings"] = user.patient_profile.readings.all()[:5]
        context["recent_prescriptions"] = user.patient_profile.prescriptions.all()[:5]
    elif user.role == User.Role.DOCTOR and hasattr(user, "doctor_profile"):
        context["profile"] = user.doctor_profile
        context["patient_count"] = PatientProfile.objects.count()
    return render(request, f"core/dashboard_{_template_key(user)}.html", context)


def _template_key(user):
    mapping = {
        User.Role.ADMINISTRATOR: "admin",
        User.Role.PATIENT: "patient",
        User.Role.DOCTOR: "doctor",
        User.Role.EMERGENCY: "emergency",
        User.Role.DEPARTMENT: "department",
    }
    return mapping.get(user.role, "generic")
