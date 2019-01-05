from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """" Class for displaying custom user model on admin site"""
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_active')}),
        ('Personal info',
         {'fields': ('fname', 'lname', 'birthdate', 'gender')}),
        ('Avatar', {'fields': ('profile_image',)})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'age', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
