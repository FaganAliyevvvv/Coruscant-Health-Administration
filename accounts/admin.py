from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CHAUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "is_approved", "is_active")
    list_filter = ("role", "is_approved", "is_active")
    actions = ["approve_users"]
    fieldsets = UserAdmin.fieldsets + (
        ("Coruscant Health", {"fields": ("role", "is_approved", "phone_number")}),
    )

    @admin.action(description="Approve selected accounts")
    def approve_users(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} account(s) approved.")
