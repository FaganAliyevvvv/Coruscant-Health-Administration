from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from doctors.models import DoctorProfile
from patients.models import PatientProfile

from .models import ServiceOrder


class ServiceOrderWorkflowTests(TestCase):
    def setUp(self):
        doctor_user = User.objects.create_user(username="drorder", password="pw", role=User.Role.DOCTOR, is_approved=True)
        self.doctor = DoctorProfile.objects.create(user=doctor_user, specialty="Radiology", license_number="RAD-1")
        patient_user = User.objects.create_user(username="ptorder", password="pw", role=User.Role.PATIENT)
        self.patient = PatientProfile.objects.create(user=patient_user, date_of_birth="1990-01-01")
        self.department_user = User.objects.create_user(
            username="deptimaging", password="pw", role=User.Role.DEPARTMENT, is_approved=True
        )
        self.order = ServiceOrder.objects.create(
            doctor=self.doctor, patient=self.patient, order_type=ServiceOrder.OrderType.CT_SCAN
        )

    def test_pending_order_appears_in_queue(self):
        self.client.login(username="deptimaging", password="pw")
        response = self.client.get(reverse("orders:order_queue"))
        self.assertIn(self.order, response.context["pending"])

    def test_department_can_accept_order(self):
        self.client.login(username="deptimaging", password="pw")
        self.client.post(reverse("orders:accept_order", args=[self.order.id]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ServiceOrder.Status.IN_PROGRESS)
        self.assertEqual(self.order.assigned_department, self.department_user)

    def test_department_can_complete_order(self):
        self.order.mark_in_progress(self.department_user)
        self.client.login(username="deptimaging", password="pw")
        response = self.client.post(
            reverse("orders:complete_order", args=[self.order.id]), {"result_text": "No abnormalities found."}
        )
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ServiceOrder.Status.COMPLETED)
        self.assertEqual(self.order.result_text, "No abnormalities found.")
        self.assertIsNotNone(self.order.completed_at)

    def test_unapproved_department_cannot_access_queue(self):
        unapproved = User.objects.create_user(username="deptnew", password="pw", role=User.Role.DEPARTMENT)
        self.client.login(username="deptnew", password="pw")
        response = self.client.get(reverse("orders:order_queue"), follow=True)
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_department_cannot_complete_order_not_assigned_to_them(self):
        other_department = User.objects.create_user(
            username="deptother", password="pw", role=User.Role.DEPARTMENT, is_approved=True
        )
        self.order.mark_in_progress(self.department_user)
        self.client.login(username="deptother", password="pw")
        response = self.client.get(reverse("orders:complete_order", args=[self.order.id]))
        self.assertEqual(response.status_code, 404)
