from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SupportSession, SupportMessage

@admin.register(SupportSession)
class SupportSessionAdmin(ModelAdmin):
    list_display = ('id', 'user', 'agent', 'subject', 'status', 'created_at')
    
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'subject')
    readonly_fields = ('created_at',)
    
    list_select_related = ('user', 'agent')
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True

@admin.register(SupportMessage)
class SupportMessageAdmin(ModelAdmin):
    list_display = ('id', 'session', 'sender', 'created_at', 'is_read')
    
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'content')
    readonly_fields = ('created_at',)
    
    list_select_related = ('session', 'sender')
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True