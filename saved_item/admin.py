from django.contrib import admin
from unfold.admin import ModelAdmin
from bns_goiteens.models import SavedItem
from django.contrib.postgres.fields import ArrayField
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget

@admin.register(SavedItem)
class CustomSavedItemClass(ModelAdmin):
    list_disply = ('user', 'content_object')
    fieldsets = ((
        None, {
            'classes' : ('wide',),
            'fields' : ('user', 'content_type', 'object_id', 'get_content_object', 'saved_at',),
        }
    ),)
    readonly_fields = ('get_content_object', 'saved_at',)
    
    add_fieldsets = ((
        None, {
            'classes' : ('wide',),
            'fields' : ('user', 'content_type', 'object_id',),
        }
    ),)
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    
    list_filter = ('user',)
    search_fields = (
        'user__username',
    )
    ordering = ('-saved_at',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }
    
    def get_content_object(self, obj):
        return obj.content_object
    get_content_object.short_description = "Content object"