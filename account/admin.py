from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models.users import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar', 
                                         'phone_number', 'date_of_birth', 'gender', 'bio')}),
        (_('Address'), {'fields': ('address', 'city', 'state', 'country', 'postal_code')}),
        (_('Family info'), {'fields': ('family_role', 'family_branch')}),
        (_('Social media'), {'fields': ('facebook', 'twitter', 'instagram', 'linkedin')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                        'is_verified', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_activity')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_verified')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'gender')
