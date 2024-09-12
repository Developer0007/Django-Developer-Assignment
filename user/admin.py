# myapp/admin.py
from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    list_filter = ('is_active', 'is_staff', 'is_superuser')

admin.site.register(User, UserAdmin)
