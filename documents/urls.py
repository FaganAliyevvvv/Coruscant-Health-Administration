from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("patient/<int:patient_id>/upload/", views.upload_document, name="upload"),
    path("patient/<int:patient_id>/", views.list_documents, name="list"),
    path("<int:doc_id>/download/", views.download_document, name="download"),
]
