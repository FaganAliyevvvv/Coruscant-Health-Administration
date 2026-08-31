from django.contrib import admin

from .models import DoctorProfile, Prescription


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "license_number")
    search_fields = ("user__username", "license_number")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "doctor", "condition_assessment", "created_at")
    list_filter = ("condition_assessment",)
