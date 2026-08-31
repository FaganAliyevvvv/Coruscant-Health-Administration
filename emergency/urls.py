from django.urls import path

from . import views

app_name = "emergency"

urlpatterns = [
    path("intake/", views.intake, name="intake"),
]
