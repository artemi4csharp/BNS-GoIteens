from re import M
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Comment, Location, Message, Promotion, Discount, Rating, SavedItem, PromoCode, Category, Item
from django.contrib.postgres.fields import ArrayField
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
import random
import string
from django import forms
from django.utils import timezone

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


class PromoCodeAdminForm(forms.ModelForm):
    confirmation_code = forms.CharField(
        max_length=10,
        label="Код підтвердження",
        help_text="Введіть код підтвердження для створення промокоду"
    )

    STATIC_CONFIRMATION_CODE = "ADMIN123"  # Статичний код підтвердження

    class Meta:
        model = PromoCode
        fields = '__all__'
        exclude = ['used_count', 'created_at']

    def __init__(self, *args, **kwargs):
        # Витягуємо request з kwargs перед викликом super()
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Встановлюємо статичний код як значення за замовчуванням
        self.fields['confirmation_code'].initial = self.STATIC_CONFIRMATION_CODE
        self.fields['confirmation_code'].widget.attrs['readonly'] = True

    def clean_confirmation_code(self):
        confirmation_code = self.cleaned_data.get('confirmation_code')
        # Перевіряємо зі статичним кодом
        if confirmation_code != self.STATIC_CONFIRMATION_CODE:
            raise forms.ValidationError("Невірний код підтвердження")
        return confirmation_code

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if PromoCode.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Промокод з таким кодом вже існує")
        return code


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    form = PromoCodeAdminForm
    list_display = ('code', 'promo_type', 'value', 'is_active', 'used_count', 'max_uses', 'valid_to')
    list_filter = ('promo_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('code', 'promo_type', 'value', 'is_active', 'confirmation_code')
        }),
        ('Обмеження', {
            'fields': ('max_uses', 'valid_from', 'valid_to')
        }),
        ('Додатково', {
            'fields': ('target_item', 'target_category'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('used_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True

    def get_form(self, request, obj=None, **kwargs):
        # Передаємо request через kwargs для форми
        Form = super().get_form(request, obj, **kwargs)

        class FormWithRequest(Form):
            def __init__(self, *args, **inner_kwargs):
                inner_kwargs['request'] = request
                super().__init__(*args, **inner_kwargs)

        return FormWithRequest

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
