from django.conf import settings
from django.db import models
from django.utils import timezone


class ServiceOrder(models.Model):
    """An order entered by a Doctor for a Department to execute (CT scan, PET scan, etc.)."""

    class OrderType(models.TextChoices):
        CT_SCAN = "CT_SCAN", "CT Scan"
        PET_SCAN = "PET_SCAN", "PET Scan"
        MRI = "MRI", "MRI"
        XRAY = "XRAY", "X-Ray"
        BLOOD_TEST = "BLOOD_TEST", "Blood Test"
        ULTRASOUND = "ULTRASOUND", "Ultrasound"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Priority(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine"
        URGENT = "URGENT", "Urgent"
        STAT = "STAT", "Stat (Immediate)"

    doctor = models.ForeignKey("doctors.DoctorProfile", on_delete=models.CASCADE, related_name="orders_placed")
    patient = models.ForeignKey("patients.PatientProfile", on_delete=models.CASCADE, related_name="service_orders")
    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.ROUTINE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    clinical_notes = models.TextField(blank=True)
    assigned_department = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_orders"
    )
    result_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_in_progress(self, department_user):
        self.status = self.Status.IN_PROGRESS
        self.assigned_department = department_user
        self.save(update_fields=["status", "assigned_department"])

    def complete(self, result_text):
        self.status = self.Status.COMPLETED
        self.result_text = result_text
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "result_text", "completed_at"])

    def __str__(self):
        return f"{self.get_order_type_display()} for {self.patient} [{self.status}]"
