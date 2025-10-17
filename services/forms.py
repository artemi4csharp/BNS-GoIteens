# services/forms.py
from django import forms
from django.forms import modelform_factory, modelformset_factory
from bns_goiteens.models import Category, Location, Service, Rating, Promotion, SavedItem, Message, Item
from bns_goiteens.models import Service as ServiceModel


class ServiceCreationForm(forms.ModelForm):
    class Meta:
        model = ServiceModel
        fields = ['name', 'description', 'price', 'category', 'location', 'service_type', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'capitalize-first input1', 'placeholder': 'Назва'}),
            'description': forms.Textarea(attrs={'class': 'capitalize-first input2', 'placeholder': 'Опис'}),
            'price': forms.NumberInput(attrs={'class': 'input4', 'placeholder': 'Ціна'}),
            'category': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'location': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'service_type': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'image': forms.FileInput(attrs={
                'id': 'id_image_input',
                'style': 'display:none;'
            }),
        }


class ServiceEditForm(forms.ModelForm):
    class Meta:
        model = ServiceModel
        fields = ['name', 'description', 'price', 'category', 'location', 'service_type', 'image', 'is_active']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'capitalize-first input1', 'placeholder': 'Назва'}),
            'description': forms.Textarea(attrs={'class': 'capitalize-first input2', 'placeholder': 'Опис'}),
            'price': forms.NumberInput(attrs={'class': 'input4', 'placeholder': 'Ціна'}),
            'category': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'location': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'service_type': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'image': forms.FileInput(attrs={
                'id': 'id_image_input',
                'style': 'display:none;'
            }),
        }

CategoryForm = modelform_factory(
    Category,
    fields = ['name', 'is_active'],
    labels = {'name':'Назва товару', 'is_active': 'Чи активна категорія'}
)

LocationForm = modelform_factory(
    Location,
    fields = ['city', 'region', 'country'],
    labels = {'city':'Місто', 'region':'Область', 'country': 'Країна'}
)

ItemCreationForm = modelform_factory(
    Item,
    fields = ['name', 'description', 'price', 'category', 'owner', 'location', 'image'],
    labels = {'name': 'Назва', 'description': 'Опис', 'price': 'Ціна', 'category':'Категорія', 'owner': 'Власник', 'location': 'Розміщення', 'image': 'Фото'},
)

ItemEditForm = modelformset_factory(
    Item,
    fields = ['name', 'description', 'price', 'image'],
    extra = 1,
    can_delete = True
)

# Видалено дубльовані форми, що викликали конфлікти

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('value',)  # Виправлено: використано кортеж замість списку
        widgets = {
            'value': forms.RadioSelect(choices=[(i, '⭐' * i) for i in range(1, 6)])
        }

PromotionCreationForm = modelform_factory(
    Promotion,
    fields = ['name', 'description', 'start_date', 'end_date', 'is_active'],
    labels = {'name': 'Назва', 'description': 'Опис', 'start_date': 'Дата початку', 'end_date': 'Дата закінчення', 'is_active': 'Чи активне'}
)

SavedItemCreationForm = modelform_factory(
    SavedItem,
    fields = ['object_id'],
    labels = {'object_id': 'ID товару'}
)

MessageCreationForm = modelform_factory(
    Message,
    fields = ['content', 'receiver', 'read'],
    labels = {'content': 'Вміст', 'receiver': 'отримувач', 'read': 'Прочитано'}
)
