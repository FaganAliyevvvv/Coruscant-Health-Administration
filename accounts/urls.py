from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CHALoginView.as_view(), name="login"),
    path("logout/", views.CHALogoutView.as_view(), name="logout"),
    path("register/", views.register_choice, name="register_choice"),
    path("register/patient/", views.register_patient, name="register_patient"),
    path("register/doctor/", views.register_doctor, name="register_doctor"),
    path("register/department/", views.register_department, name="register_department"),
]
