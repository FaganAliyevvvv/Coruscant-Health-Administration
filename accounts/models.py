from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Coruscant Health Administration system user.

    Every account has a role. Patient, Doctor, and Department accounts are
    created in an unapproved state and cannot use their role-specific
    dashboards until an Administrator approves them - this satisfies the
    requirement that patients/doctors "register with the acknowledgment
    from the administrator."
    """

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
        ADMINISTRATOR = "ADMINISTRATOR", "Administrator"
        EMERGENCY = "EMERGENCY", "Emergency Services"
        DEPARTMENT = "DEPARTMENT", "Department"

    role = models.CharField(max_length=20, choices=Role.choices)
    is_approved = models.BooleanField(
        default=False,
        help_text="Administrator sign-off required before Patient/Doctor/Department accounts are active.",
    )
    phone_number = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def approve(self):
        self.is_approved = True
        self.save(update_fields=["is_approved"])

    @property
    def needs_approval(self):
        return self.role in (self.Role.PATIENT, self.Role.DOCTOR, self.Role.DEPARTMENT) and not self.is_approved

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
