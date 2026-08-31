from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models

from .crypto import decrypt_bytes, encrypt_bytes


def encrypted_upload_path(instance, filename):
    return f"encrypted_documents/patient_{instance.patient_id}/{filename}.enc"


class EncryptedDocument(models.Model):
    """
    A patient or doctor uploaded document (lab result scan, imaging report,
    referral letter, etc.), stored encrypted at rest.
    """

    patient = models.ForeignKey("patients.PatientProfile", on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    related_order = models.ForeignKey(
        "orders.ServiceOrder", null=True, blank=True, on_delete=models.SET_NULL, related_name="documents"
    )
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, blank=True)
    encrypted_file = models.FileField(upload_to=encrypted_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    @classmethod
    def store(cls, *, patient, uploaded_by, uploaded_file, related_order=None):
        """Encrypt an uploaded Django File and persist it."""
        plaintext = uploaded_file.read()
        ciphertext = encrypt_bytes(plaintext)
        doc = cls(
            patient=patient,
            uploaded_by=uploaded_by,
            related_order=related_order,
            original_filename=uploaded_file.name,
            content_type=getattr(uploaded_file, "content_type", "") or "",
        )
        doc.encrypted_file.save(uploaded_file.name, ContentFile(ciphertext), save=False)
        doc.save()
        return doc

    def decrypted_bytes(self) -> bytes:
        self.encrypted_file.open("rb")
        try:
            ciphertext = self.encrypted_file.read()
        finally:
            self.encrypted_file.close()
        return decrypt_bytes(ciphertext)

    def __str__(self):
        return f"{self.original_filename} for {self.patient}"
