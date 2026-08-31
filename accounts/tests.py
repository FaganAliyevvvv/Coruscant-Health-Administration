from django.test import TestCase
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def test_patient_and_doctor_require_approval_by_default(self):
        patient = User.objects.create_user(username="pat1", password="pw", role=User.Role.PATIENT)
        doctor = User.objects.create_user(username="doc1", password="pw", role=User.Role.DOCTOR)
        self.assertTrue(patient.needs_approval)
        self.assertTrue(doctor.needs_approval)

    def test_administrator_does_not_need_approval(self):
        admin = User.objects.create_user(username="admin1", password="pw", role=User.Role.ADMINISTRATOR)
        self.assertFalse(admin.needs_approval)

    def test_approve_flips_flag(self):
        patient = User.objects.create_user(username="pat2", password="pw", role=User.Role.PATIENT)
        self.assertFalse(patient.is_approved)
        patient.approve()
        patient.refresh_from_db()
        self.assertTrue(patient.is_approved)
        self.assertFalse(patient.needs_approval)


class RegistrationFlowTests(TestCase):
    def test_patient_registration_creates_unapproved_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:register_patient"),
            {
                "username": "newpatient",
                "first_name": "Anakin",
                "last_name": "Skywalker",
                "email": "anakin@example.com",
                "phone_number": "",
                "date_of_birth": "2000-01-01",
                "device_id": "DEV-001",
                "password1": "TestPass123!",
                "password2": "TestPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newpatient")
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertFalse(user.is_approved)
        self.assertTrue(hasattr(user, "patient_profile"))

    def test_doctor_registration_creates_unapproved_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:register_doctor"),
            {
                "username": "newdoctor",
                "first_name": "Harribore",
                "last_name": "Onuta",
                "email": "onuta@example.com",
                "phone_number": "",
                "specialty": "Infectious Disease",
                "license_number": "LIC-999",
                "password1": "TestPass123!",
                "password2": "TestPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newdoctor")
        self.assertEqual(user.role, User.Role.DOCTOR)
        self.assertFalse(user.is_approved)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            username="patientx", password="pw", role=User.Role.PATIENT, is_approved=False
        )
        from patients.models import PatientProfile

        PatientProfile.objects.create(user=self.patient, date_of_birth="1990-01-01")

    def test_unapproved_patient_redirected_from_upload(self):
        self.client.login(username="patientx", password="pw")
        response = self.client.get(reverse("patients:upload_reading"), follow=True)
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_wrong_role_cannot_access_doctor_area(self):
        self.client.login(username="patientx", password="pw")
        response = self.client.get(reverse("doctors:patient_list"), follow=True)
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("patients:upload_reading"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
