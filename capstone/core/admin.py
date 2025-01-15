
from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    # Configuration for CustomUserAdmin
    list_display = ('email', 'name', 'user_type', 'is_active', 'is_superuser')
    search_fields = ('email', 'name')
    list_filter = ('user_type', 'is_active', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)