from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("readings/upload/", views.upload_reading, name="upload_reading"),
    path("readings/", views.my_readings, name="my_readings"),
    path("prescriptions/", views.my_prescriptions, name="my_prescriptions"),
]
