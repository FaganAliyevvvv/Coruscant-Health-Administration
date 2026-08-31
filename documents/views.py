from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from patients.models import PatientProfile

from .forms import DocumentUploadForm
from .models import EncryptedDocument


def _can_access_patient_documents(user, patient: PatientProfile) -> bool:
    if user.role == User.Role.ADMINISTRATOR:
        return True
    if user.role == User.Role.PATIENT:
        return hasattr(user, "patient_profile") and user.patient_profile.id == patient.id
    if user.role == User.Role.DOCTOR:
        return hasattr(user, "doctor_profile")  # any approved doctor may view, per hospital-wide access model
    return False


@login_required
def upload_document(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not _can_access_patient_documents(request.user, patient):
        raise PermissionDenied
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            EncryptedDocument.store(
                patient=patient, uploaded_by=request.user, uploaded_file=form.cleaned_data["file"]
            )
            messages.success(request, "Document uploaded and encrypted at rest.")
            return redirect("documents:list", patient_id=patient.id)
    else:
        form = DocumentUploadForm()
    return render(request, "documents/upload.html", {"form": form, "patient": patient})


@login_required
def list_documents(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    if not _can_access_patient_documents(request.user, patient):
        raise PermissionDenied
    documents = patient.documents.all()
    return render(request, "documents/list.html", {"documents": documents, "patient": patient})


@login_required
def download_document(request, doc_id):
    document = get_object_or_404(EncryptedDocument, pk=doc_id)
    if not _can_access_patient_documents(request.user, document.patient):
        raise PermissionDenied
    plaintext = document.decrypted_bytes()
    response = HttpResponse(plaintext, content_type=document.content_type or "application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{document.original_filename}"'
    return response
