from django import forms

from accounts.models import User


class EmergencyIntakeForm(forms.Form):
    """Minimal-friction form so Emergency Services staff can register a new
    patient in seconds. Auto-approved (no waiting on an Administrator) since
    the patient needs to be in the system immediately."""

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False)
    chief_complaint = forms.CharField(widget=forms.Textarea, required=False)
    triage_priority = forms.ChoiceField(
        choices=[("CRITICAL", "Critical"), ("URGENT", "Urgent"), ("STANDARD", "Standard")]
    )
