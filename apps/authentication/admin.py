from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.db import transaction
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'fullname', 'cin', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('fullname', 'cin', 'email', 'birthdate', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'fullname', 'cin', 'email', 'is_active', 'is_staff')
        }),
    )
    search_fields = ('email', 'username', 'cin')
    ordering = ('username',)

    def delete_model(self, request, obj):
        with transaction.atomic():
            # Delete or handle related objects before deleting the user
            # For example, obj.relatedmodel_set.all().delete() for any related models
            super().delete_model(request, obj)
