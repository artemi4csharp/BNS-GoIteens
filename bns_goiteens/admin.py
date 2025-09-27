from re import M
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Comment, Location, Message, Promotion, Discount, Rating, SavedItem
from django.contrib.postgres.fields import ArrayField
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget

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
    list_filter = ('country',)
    search_fields = (
        'country',
        'region',
        'city',
    )
    ordering = ('country',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }
    

@admin.register(Comment)
class CustomCommentClass(ModelAdmin):
    model = Comment
    list_display = ('author', 'content_type', 'object_id', 'content_object', 'created_at',)
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
    list_filter = ('author',)
    search_fields = (
        'text',
        'author__username',
    )
    ordering = ('-created_at',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }
    
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
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    list_filter = ('user', 'value')
    search_fields = (
    'user__username',
    )
    ordering = ('user',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }


@admin.register(Promotion)
class CustomPromotionClass(ModelAdmin):
    list_display = ('name', 'description', 'start_date', 'end_date', 'is_active',)
    fieldsets = ((
      None, {
          'classes' : ('wide',),
          'fields' : ('name', 'description', 'start_date', 'end_date', 'is_active',)
      }  
    ),)
    add_fieldsets = ((
      None, {
          'classes' : ('wide',),
          'fields' : ('name', 'description', 'start_date', 'end_date', 'is_active',)
      }    
    ),)
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    list_filter = ('start_date', 'end_date', 'is_active')
    search_fields = (
    'name',
    'description'
    )
    ordering = ('-end_date',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }


@admin.register(Discount)
class CustomDiscountClass(ModelAdmin):
    list_display = ('promotion', 'discount_type', 'value', 'item', 'category',)
    fieldsets = ((
      None, {
          'classes' : ("wide",),
          'fields' : ('promotion', 'discount_type', 'value', 'item', 'category',),
      }  
    ),)
    add_fieldsets = ((
      None, {
          'classes' : ("wide",),
          'fields' : ('promotion', 'discount_type', 'value', 'item', 'category',),
      }    
    ),)
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    list_filter = ('promotion', 'discount_type', 'item')
    search_fields = (
    'value',
    'category__name'
    )
    ordering = ('-value',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }

@admin.register(Message)
class CustomMessageClass(ModelAdmin):
    model = Message
    list_display = ('sender', 'receiver', 'created_at', 'updated_at')
    fieldsets = ((
      None, {
          "classes" : ('wide',),
          "fields" : ('content', 'sender', 'receiver', 'read', 'created_at', 'updated_at'),
      }  
    ),) 
    readonly_fields = ('read', 'created_at', 'updated_at',)
    add_fieldsets = ((
      None, {
          "classes" : ('wide',),
          "fields" : ('content', 'sender', 'receiver'), 
      }  
    ),)
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    list_filter = ('sender', 'receiver',)
    search_fields = (
        'sender__username',
        'receiver__username',
    )
    ordering = ('-created_at',)
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }