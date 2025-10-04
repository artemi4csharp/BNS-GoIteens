from django.forms import forms
from django.forms import modelform_factory, inlineformset_factory, modelformset_factory
from .models import Category, Location, Item, Service, Rating, Promotion, SavedItem, Message

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
    labels = {'name': 'Назва', 'decription': 'Опис', 'price': 'Ціна', 'category':'Категорія', 'owner': 'Власник', 'location': 'Розміщення', 'image': 'Фото'},
)

ItemEditForm = modelformset_factory(
    Item,
    fields = ['name', 'description', 'price', 'image'],
    extra = 1,
    can_delete = True
    )

ServiceCreationForm = modelform_factory(
    Service,
    fields = ['name', 'description', 'price', 'category', 'owner', 'location', 'image'],
    labels = {'name': 'Назва', 'description': 'Опис', 'price': 'Ціна', 'category':'Категорія', 'owner': 'Власник', 'location': 'Розміщення', 'image': 'Фото'},
)

ServiceEditForm = modelformset_factory(
    Service,
    fields = ['name', 'description', 'price', 'image'],
    extra = 1,
    can_delete = True
    )


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value'],
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