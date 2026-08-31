from django.conf import settings
from django.db import models


class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    specialty = models.CharField(max_length=120)
    license_number = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.specialty})"


class Prescription(models.Model):
    """A doctor's written report / prescribed course of action for a patient."""

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="prescriptions")
    patient = models.ForeignKey("patients.PatientProfile", on_delete=models.CASCADE, related_name="prescriptions")
    title = models.CharField(max_length=200)
    report_text = models.TextField()
    condition_assessment = models.CharField(
        max_length=20,
        choices=[
            ("IMPROVING", "Improving"),
            ("STABLE", "Stable"),
            ("WORSENING", "Worsening"),
            ("UNKNOWN", "Unknown"),
        ],
        default="UNKNOWN",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} for {self.patient} by {self.doctor}"
