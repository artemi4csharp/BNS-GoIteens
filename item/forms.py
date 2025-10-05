from django import forms
from django.forms import modelform_factory
from bns_goiteens.models import Category, Location, Item, Service, Rating, Promotion, SavedItem, Message
from .models import CategoryRequest, Category

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

class ItemEditForm(forms.ModelForm):
    class Meta: 
        model = Item 
        fields = ['name', 'description', 'price', 'image']

ServiceCreationForm = modelform_factory(
    Service, 
    fields = ['name', 'description', 'price', 'category', 'owner', 'location', 'service_type', 'image'],
    labels = {'name': 'Назва', 'description': 'Опис', 'price': 'Ціна', 'category':'Категорія', 'owner': 'Власник', 'location': 'Розміщення', 'image': 'Фото'}, 
)

class ServiceEditForm(forms.ModelForm):
    class Meta: 
        model = Service 
        fields = ['name', 'description', 'price', 'service_type', 'image']


class RatingForm(forms.ModelForm):
    class Meta: 
        model = Rating
        fields = ['value']
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

class CategoryRequestForm(forms.ModelForm):
    class Meta:
        model = CategoryRequest
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Нова категорія'}),
            'parent': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.all()
        self.fields['parent'].required = False