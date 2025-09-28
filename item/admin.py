from django.contrib import admin
from unfold.admin  import ModelAdmin
from bns_goiteens.models import Item
from django.contrib.postgres.fields import ArrayField
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget

@admin.register(Item)
class CustomItemClass(admin.ModelAdmin):
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
    list_filter = ('owner', 'category',)
    search_fields = (
        "name",
        "description",
        "category__name",
        "owner__username",
        "owner__email",
        "location__city", 
    )
    ordering = ('name',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }