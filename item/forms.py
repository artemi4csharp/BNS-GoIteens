from django import forms
from django.forms import modelform_factory
from bns_goiteens.models import Category,CategoryRequest, Complaint, Location, Item, Service, Rating, Promotion, SavedItem, Message, Comment

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

class ItemCreationForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'category', 'location', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'capitalize-first input1', 'placeholder': 'Назва'}),
            'description': forms.Textarea(attrs={'class': 'capitalize-first input2', 'placeholder': 'Опис'}),
            'price': forms.NumberInput(attrs={'class': 'input4', 'placeholder': 'Ціна'}),
            'category': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'location': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'image': forms.FileInput(attrs={
                'id': 'id_image_input',
                'style': 'display:none;'
            }),
        }

class ItemEditForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'category', 'location', 'image']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'capitalize-first input1', 'placeholder': 'Назва'}),
            'description': forms.Textarea(attrs={'class': 'capitalize-first input2', 'placeholder': 'Опис'}),
            'price': forms.NumberInput(attrs={'class': 'input4', 'placeholder': 'Ціна'}),
            'category': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'location': forms.Select(attrs={'class': 'capitalize-first input3'}),
            'image': forms.FileInput(attrs={
                'id': 'id_image_input',
                'style': 'display:none;'
            }),
        }

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

class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'comment-text',
            'placeholder': "Введіть ваш коментар...",
            'rows': 4,
            'class': 'comment_textarea',
        }),
        label="Текст коментаря"
    )

    class Meta:
        model = Comment
        fields = ['text']


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


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Опишіть причину скарги...'}),
        }
