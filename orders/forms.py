from django import forms

from .models import ServiceOrder


class CompleteOrderForm(forms.Form):
    result_text = forms.CharField(widget=forms.Textarea, label="Results / findings")
