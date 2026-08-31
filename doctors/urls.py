from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/<int:patient_id>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:patient_id>/prescribe/", views.write_prescription, name="write_prescription"),
    path("patients/<int:patient_id>/order/", views.create_order, name="create_order"),
]
