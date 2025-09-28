from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from bns_goiteens.models import User  # Імпорт кастомної моделі User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    model = User
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ('username', 'email', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )
    compressed_fields = True
    warn_unsaved_form = True
    list_fullwidth = True
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }