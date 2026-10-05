from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "full_name", "is_admin", "is_staff", "date_joined")
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительно", {"fields": ("full_name", "is_admin", "storage_path")}),
    )
