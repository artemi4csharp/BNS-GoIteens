from django.contrib import admin
from unfold.admin  import ModelAdmin
from bns_goiteens.models import Item

@admin.register(Item)
class CustomItemClass(ModelAdmin):
    model = Item
    list_display = ('name', 'price', 'category', 'owner', 'get_avg_rating','created_at', 'updated_at')
    fieldsets = (
        ("Main", {
            "classes" : ("wide",),
            "fields" : ('name', 'price', 'category', 'owner', 'location', 'image', 'created_at', 'updated_at', 'get_avg_rating'),
            }),
    )
    add_fieldsets = (
        ("Main", {
        "classes" : ("wide",),
        "fields" : ('name', 'price', 'category', 'owner', 'location', 'image'),
        }),
    )
    readonly_fields = ("created_at", "updated_at", "get_avg_rating")
    def get_avg_rating(self, obj):
        return obj.average_rating()
    get_avg_rating.short_description = "Rating"
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True