from django.conf import settings
from django.db import models


class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile")
    mrn = models.CharField("Medical Record Number", max_length=20, unique=True, blank=True)
    date_of_birth = models.DateField()
    device_id = models.CharField(max_length=64, blank=True, help_text="Wearable/monitoring device serial number.")
    primary_doctor = models.ForeignKey(
        "doctors.DoctorProfile", null=True, blank=True, on_delete=models.SET_NULL, related_name="primary_patients"
    )

    def save(self, *args, **kwargs):
        if not self.mrn:
            # Simple sequential-looking MRN; uniqueness enforced by DB constraint + retry.
            from django.db import IntegrityError, transaction

            for _ in range(5):
                candidate = f"CHA-{self.user_id or 0:05d}{PatientProfile.objects.count() + 1:04d}"
                self.mrn = candidate
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    continue
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.mrn})"


class DeviceReading(models.Model):
    """A single batch of vitals uploaded from the patient's attached device."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="readings")
    recorded_at = models.DateTimeField(help_text="When the device captured the reading.")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    heart_rate_bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    systolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    diastolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    spo2_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-recorded_at"]

    def is_out_of_range(self):
        """Very simple clinical flagging so a doctor can spot trouble at a glance."""
        flags = []
        if self.heart_rate_bpm and not (50 <= self.heart_rate_bpm <= 110):
            flags.append("heart rate")
        if self.spo2_percent and self.spo2_percent < 94:
            flags.append("SpO2")
        if self.temperature_c and not (35.5 <= float(self.temperature_c) <= 38.3):
            flags.append("temperature")
        if self.systolic_bp and not (90 <= self.systolic_bp <= 140):
            flags.append("systolic BP")
        return flags

    def __str__(self):
        return f"Reading for {self.patient} @ {self.recorded_at:%Y-%m-%d %H:%M}"
