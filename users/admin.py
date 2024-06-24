from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('middle_name', 'avatar',)}),
    )
    list_display = ( 'username', 'first_name', 'last_name',)

admin.site.register(CustomUser, CustomUserAdmin)
