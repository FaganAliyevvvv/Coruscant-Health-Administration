import uuid
from datetime import date

from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User
from patients.models import PatientProfile

from .forms import EmergencyIntakeForm
from .models import EmergencyIntake


@role_required(User.Role.EMERGENCY)
def intake(request):
    if request.method == "POST":
        form = EmergencyIntakeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = f"patient_{uuid.uuid4().hex[:10]}"
            user = User.objects.create_user(
                username=username,
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=User.Role.PATIENT,
                is_approved=True,  # emergency intake bypasses the usual approval wait
            )
            user.set_unusable_password()
            user.save()
            profile = PatientProfile.objects.create(
                user=user, date_of_birth=data.get("date_of_birth") or date(1900, 1, 1)
            )
            EmergencyIntake.objects.create(
                patient=profile,
                intake_by=request.user,
                chief_complaint=data.get("chief_complaint", ""),
                triage_priority=data["triage_priority"],
            )
            messages.success(request, f"Patient {profile} registered and ready for triage.")
            return redirect("emergency:intake")
    else:
        form = EmergencyIntakeForm()
    recent = EmergencyIntake.objects.select_related("patient__user").order_by("-created_at")[:15]
    return render(request, "emergency/intake.html", {"form": form, "recent": recent})
