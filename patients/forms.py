from django import forms

from .models import DeviceReading


class DeviceReadingForm(forms.ModelForm):
    class Meta:
        model = DeviceReading
        fields = [
            "recorded_at",
            "heart_rate_bpm",
            "systolic_bp",
            "diastolic_bp",
            "temperature_c",
            "spo2_percent",
            "notes",
        ]
        widgets = {"recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}
