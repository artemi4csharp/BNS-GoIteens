from django.contrib import admin
from unfold.admin  import ModelAdmin
from bns_goiteens.models import Service
from django.utils.html import format_html

@admin.register(Service)
class CustomServiceClass(ModelAdmin):
    model = Service
    list_display = ('name', 'price', 'category', 'owner','service_type', 'created_at', 'updated_at')
    fieldsets = (
        ("Main", {
            "classes" : ("wide",),
            "fields" : ('name', 'price', 'category', 'owner', 'location', 'image', 'image_preview','get_avg_rating', 'service_type', 'created_at', 'updated_at', ),
            }),
    )
    add_fieldsets = (
        ("Main", {
        "classes" : ("wide",),
        "fields" : ('name', 'price', 'category', 'owner', 'location', 'image', 'service_type'),
        }),
    )
    readonly_fields = ("created_at", "updated_at", "get_avg_rating", "image_preview")
    
    def get_avg_rating(self, obj):
        return obj.average_rating()
    get_avg_rating.short_description = "Rating"
    
    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, "url"):
            return format_html('<img src="{}" style="max-height:200px; max-width:200px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Image preview"
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True