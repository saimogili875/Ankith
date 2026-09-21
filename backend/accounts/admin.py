from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'target_exam', 'target_year', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('target_exam', 'target_year', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('EdTech Profile', {'fields': ('target_exam', 'target_year')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('EdTech Profile', {'fields': ('target_exam', 'target_year')}),
    )
