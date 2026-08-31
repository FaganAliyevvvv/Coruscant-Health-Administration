from django import forms

from orders.models import ServiceOrder

from .models import Prescription


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["title", "report_text", "condition_assessment"]


class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ["order_type", "priority", "clinical_notes"]
