from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Comment, Location, Message, Promotion, Discount, Rating, SavedItem

@admin.register(Category)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(Location)
class CustomLocationClass(ModelAdmin):
    model = Location
    list_display = ('country', 'region', 'city')
    add_fieldsets = (
        ("Main", {
            'classes': ('wide',),
            'fields': ('country', 'region', 'city'),
        }),
    )
    fieldsets = (
        (None, {
            'classes' : ('wide',),
            'fields' : ('country', 'region', 'city'),
        }),
    )
    list_filter = ('country', 'region', 'city')
    search_fields = ('country', 'region', 'city')
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    

@admin.register(Comment)
class CustomCommentClass(ModelAdmin):
    model = Comment
    list_display = ('text', 'author', 'content_type', 'object_id', 'content_object', 'created_at',)
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('text', 'author', 'content_type', 'object_id', 'get_content_object', 'created_at',)
        }),
    ) 
    readonly_fields = ('created_at', 'get_content_object')
    add_fieldsets = (
        (None, {
            'classes' : ('wide',),
           'fields' : ('text', 'author', 'content_type', 'object_id', 'created_at',) 
        }),
    )
    
    def get_content_object(self, obj):
        return obj.content_object
    get_content_object.short_description = "Content object"
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True

@admin.register(Rating)
class CustomRatingClass(ModelAdmin):
    model = Rating
    list_display = ('user', 'value', 'content_object')
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'value','content_type', 'object_id', 'content_object'),
        }),
    ) 
    readonly_fields = ('content_object',)

    
    def get_content_object(self, obj):
        return obj.content_object
    get_content_object.short_description = "Content object"
    
@admin.register(SavedItem)
class CustomSavedItemClass(ModelAdmin):
    pass


@admin.register(Promotion)
class CustomPromotionClass(ModelAdmin):
    pass

@admin.register(Discount)
class CustomDiscountClass(ModelAdmin):
    pass

@admin.register(Message)
class CustomMessageClass(ModelAdmin):
    pass