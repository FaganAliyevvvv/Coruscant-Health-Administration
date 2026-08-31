from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import EmergencyIntake


class EmergencyIntakeTests(TestCase):
    def setUp(self):
        self.emergency_user = User.objects.create_user(
            username="ertriage", password="pw", role=User.Role.EMERGENCY, is_approved=True
        )
        self.client.login(username="ertriage", password="pw")

    def test_intake_creates_auto_approved_patient(self):
        response = self.client.post(
            reverse("emergency:intake"),
            {
                "first_name": "Anakin",
                "last_name": "Skywalker",
                "date_of_birth": "2000-01-01",
                "chief_complaint": "Burns from lightsaber accident.",
                "triage_priority": "CRITICAL",
            },
        )
        self.assertEqual(response.status_code, 302)
        intake = EmergencyIntake.objects.get()
        self.assertEqual(intake.triage_priority, "CRITICAL")
        self.assertTrue(intake.patient.user.is_approved)
        self.assertEqual(intake.patient.user.role, User.Role.PATIENT)

    def test_non_emergency_role_cannot_access_intake(self):
        patient = User.objects.create_user(username="regularpatient", password="pw", role=User.Role.PATIENT)
        self.client.logout()
        self.client.login(username="regularpatient", password="pw")
        response = self.client.get(reverse("emergency:intake"), follow=True)
        self.assertRedirects(response, reverse("core:dashboard"))
