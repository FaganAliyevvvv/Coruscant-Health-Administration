from django.contrib import admin

from .models import EncryptedDocument


@admin.register(EncryptedDocument)
class EncryptedDocumentAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "patient", "uploaded_by", "uploaded_at")
    readonly_fields = ("encrypted_file",)
