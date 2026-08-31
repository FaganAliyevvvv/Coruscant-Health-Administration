from django.db import models


class EmergencyIntake(models.Model):
    """Audit record of a fast-tracked emergency registration, linked to the
    PatientProfile that was created for them."""

    patient = models.OneToOneField("patients.PatientProfile", on_delete=models.CASCADE, related_name="emergency_intake")
    intake_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    chief_complaint = models.TextField(blank=True)
    triage_priority = models.CharField(
        max_length=10, choices=[("CRITICAL", "Critical"), ("URGENT", "Urgent"), ("STANDARD", "Standard")]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emergency intake for {self.patient} ({self.triage_priority})"
