from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import DeviceReading, PatientProfile


class PatientProfileTests(TestCase):
    def test_mrn_auto_generated_and_unique(self):
        u1 = User.objects.create_user(username="p1", password="pw", role=User.Role.PATIENT)
        u2 = User.objects.create_user(username="p2", password="pw", role=User.Role.PATIENT)
        p1 = PatientProfile.objects.create(user=u1, date_of_birth="1990-01-01")
        p2 = PatientProfile.objects.create(user=u2, date_of_birth="1991-01-01")
        self.assertTrue(p1.mrn)
        self.assertNotEqual(p1.mrn, p2.mrn)


class DeviceReadingFlagTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="p3", password="pw", role=User.Role.PATIENT)
        self.profile = PatientProfile.objects.create(user=user, date_of_birth="1990-01-01")

    def test_normal_reading_has_no_flags(self):
        reading = DeviceReading.objects.create(
            patient=self.profile,
            recorded_at="2026-01-01T09:00:00Z",
            heart_rate_bpm=70,
            spo2_percent=98,
            temperature_c=Decimal("37.0"),
            systolic_bp=115,
        )
        self.assertEqual(reading.is_out_of_range(), [])

    def test_low_spo2_is_flagged(self):
        reading = DeviceReading.objects.create(
            patient=self.profile, recorded_at="2026-01-01T09:00:00Z", spo2_percent=88
        )
        self.assertIn("SpO2", reading.is_out_of_range())

    def test_high_heart_rate_is_flagged(self):
        reading = DeviceReading.objects.create(
            patient=self.profile, recorded_at="2026-01-01T09:00:00Z", heart_rate_bpm=160
        )
        self.assertIn("heart rate", reading.is_out_of_range())


class UploadReadingViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="approvedpatient", password="pw", role=User.Role.PATIENT, is_approved=True
        )
        self.profile = PatientProfile.objects.create(user=self.user, date_of_birth="1990-01-01")
        self.client.login(username="approvedpatient", password="pw")

    def test_approved_patient_can_upload_reading(self):
        response = self.client.post(
            reverse("patients:upload_reading"),
            {
                "recorded_at": "2026-01-01T09:00",
                "heart_rate_bpm": 72,
                "systolic_bp": 118,
                "diastolic_bp": 76,
                "temperature_c": "36.8",
                "spo2_percent": 97,
                "notes": "Feeling fine.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.profile.readings.count(), 1)

    def test_readings_list_only_shows_own_readings(self):
        other_user = User.objects.create_user(
            username="otherpatient", password="pw", role=User.Role.PATIENT, is_approved=True
        )
        other_profile = PatientProfile.objects.create(user=other_user, date_of_birth="1985-01-01")
        DeviceReading.objects.create(patient=other_profile, recorded_at="2026-01-01T09:00:00Z", heart_rate_bpm=80)
        DeviceReading.objects.create(patient=self.profile, recorded_at="2026-01-01T09:00:00Z", heart_rate_bpm=70)
        response = self.client.get(reverse("patients:my_readings"))
        self.assertEqual(len(response.context["readings"]), 1)
