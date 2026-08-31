from django.contrib import admin

from .models import ServiceOrder


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_type", "patient", "doctor", "priority", "status", "created_at")
    list_filter = ("status", "priority", "order_type")
