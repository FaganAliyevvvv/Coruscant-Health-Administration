from django.contrib import admin

from .models import DeviceReading, PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("mrn", "user", "date_of_birth", "primary_doctor")
    search_fields = ("mrn", "user__username", "user__first_name", "user__last_name")


@admin.register(DeviceReading)
class DeviceReadingAdmin(admin.ModelAdmin):
    list_display = ("patient", "recorded_at", "heart_rate_bpm", "spo2_percent")
    list_filter = ("recorded_at",)
