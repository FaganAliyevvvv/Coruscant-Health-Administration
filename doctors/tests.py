from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from orders.models import ServiceOrder
from patients.models import PatientProfile

from .models import DoctorProfile, Prescription


class DoctorWorkflowTests(TestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(
            username="drwho", password="pw", role=User.Role.DOCTOR, is_approved=True
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user, specialty="Virology", license_number="LIC-1"
        )
        self.patient_user = User.objects.create_user(username="pt1", password="pw", role=User.Role.PATIENT)
        self.patient_profile = PatientProfile.objects.create(user=self.patient_user, date_of_birth="1990-01-01")
        self.client.login(username="drwho", password="pw")

    def test_doctor_sees_patient_list(self):
        response = self.client.get(reverse("doctors:patient_list"))
        self.assertContains(response, self.patient_profile.mrn)

    def test_doctor_can_write_prescription(self):
        response = self.client.post(
            reverse("doctors:write_prescription", args=[self.patient_profile.id]),
            {
                "title": "Brainworm Rot Type A follow-up",
                "report_text": "Continue antiviral course, recheck in 5 days.",
                "condition_assessment": "IMPROVING",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Prescription.objects.count(), 1)
        self.assertEqual(Prescription.objects.first().doctor, self.doctor_profile)

    def test_doctor_can_create_service_order(self):
        response = self.client.post(
            reverse("doctors:create_order", args=[self.patient_profile.id]),
            {"order_type": "CT_SCAN", "priority": "URGENT", "clinical_notes": "Check for lesions."},
        )
        self.assertEqual(response.status_code, 302)
        order = ServiceOrder.objects.get()
        self.assertEqual(order.status, ServiceOrder.Status.PENDING)
        self.assertEqual(order.priority, "URGENT")

    def test_unapproved_doctor_is_blocked(self):
        unapproved = User.objects.create_user(username="drnew", password="pw", role=User.Role.DOCTOR)
        DoctorProfile.objects.create(user=unapproved, specialty="Surgery", license_number="LIC-2")
        self.client.logout()
        self.client.login(username="drnew", password="pw")
        response = self.client.get(reverse("doctors:patient_list"), follow=True)
        self.assertRedirects(response, reverse("core:dashboard"))
