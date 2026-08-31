from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("queue/", views.order_queue, name="order_queue"),
    path("<int:order_id>/accept/", views.accept_order, name="accept_order"),
    path("<int:order_id>/complete/", views.complete_order, name="complete_order"),
]
