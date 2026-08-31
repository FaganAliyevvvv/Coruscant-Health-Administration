import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from doctors.models import DoctorProfile
from patients.models import PatientProfile

from .crypto import decrypt_bytes, encrypt_bytes
from .models import EncryptedDocument

TEMP_MEDIA = tempfile.mkdtemp()


class CryptoRoundTripTests(TestCase):
    def test_encrypt_then_decrypt_returns_original_bytes(self):
        original = b"Patient lab result: all values within normal range."
        ciphertext = encrypt_bytes(original)
        self.assertNotEqual(ciphertext, original)
        self.assertEqual(decrypt_bytes(ciphertext), original)

    def test_ciphertext_does_not_contain_plaintext(self):
        original = b"CONFIDENTIAL: Brainworm Rot Type A positive."
        ciphertext = encrypt_bytes(original)
        self.assertNotIn(b"CONFIDENTIAL", ciphertext)
        self.assertNotIn(b"Brainworm", ciphertext)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class DocumentUploadWorkflowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.patient_user = User.objects.create_user(
            username="docpatient", password="pw", role=User.Role.PATIENT, is_approved=True
        )
        self.patient = PatientProfile.objects.create(user=self.patient_user, date_of_birth="1990-01-01")
        self.other_patient_user = User.objects.create_user(
            username="otherdocpatient", password="pw", role=User.Role.PATIENT, is_approved=True
        )
        self.other_patient = PatientProfile.objects.create(
            user=self.other_patient_user, date_of_birth="1991-01-01"
        )

    def test_patient_can_upload_and_download_own_document(self):
        self.client.login(username="docpatient", password="pw")
        upload = SimpleUploadedFile("scan.txt", b"scan contents", content_type="text/plain")
        response = self.client.post(reverse("documents:upload", args=[self.patient.id]), {"file": upload})
        self.assertEqual(response.status_code, 302)
        doc = EncryptedDocument.objects.get()
        self.assertEqual(doc.patient, self.patient)

        download = self.client.get(reverse("documents:download", args=[doc.id]))
        self.assertEqual(download.status_code, 200)
        self.assertEqual(b"".join(download.streaming_content) if download.streaming else download.content, b"scan contents")

    def test_file_stored_on_disk_is_encrypted_not_plaintext(self):
        self.client.login(username="docpatient", password="pw")
        upload = SimpleUploadedFile("secret.txt", b"top secret vitals data", content_type="text/plain")
        self.client.post(reverse("documents:upload", args=[self.patient.id]), {"file": upload})
        doc = EncryptedDocument.objects.get()
        doc.encrypted_file.open("rb")
        raw_bytes = doc.encrypted_file.read()
        doc.encrypted_file.close()
        self.assertNotIn(b"top secret vitals data", raw_bytes)

    def test_patient_cannot_access_another_patients_documents(self):
        EncryptedDocument.store(
            patient=self.other_patient,
            uploaded_by=self.other_patient_user,
            uploaded_file=SimpleUploadedFile("other.txt", b"not yours", content_type="text/plain"),
        )
        self.client.login(username="docpatient", password="pw")
        response = self.client.get(reverse("documents:list", args=[self.other_patient.id]))
        self.assertEqual(response.status_code, 403)

    def test_doctor_can_view_any_patients_documents(self):
        doctor_user = User.objects.create_user(
            username="docviewer", password="pw", role=User.Role.DOCTOR, is_approved=True
        )
        DoctorProfile.objects.create(user=doctor_user, specialty="General", license_number="GEN-1")
        EncryptedDocument.store(
            patient=self.patient,
            uploaded_by=self.patient_user,
            uploaded_file=SimpleUploadedFile("readable.txt", b"visible to doctor", content_type="text/plain"),
        )
        self.client.login(username="docviewer", password="pw")
        response = self.client.get(reverse("documents:list", args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
