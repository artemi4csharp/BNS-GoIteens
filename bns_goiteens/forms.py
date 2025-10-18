from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, PromoCode, Order, SharedOrder, Complaint
from decimal import Decimal

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'avatar', 'address', 'first_name', 'last_name']

class PromoCodeForm(forms.Form):
    code = forms.CharField(max_length=50, label="Промокод")

    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            promo = PromoCode.objects.get(code=code)
            if not promo.is_valid():
                raise forms.ValidationError("Промокод недійсний або закінчився")
        except PromoCode.DoesNotExist:
            raise forms.ValidationError("Промокод не знайдено")
        return code

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'avatar', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введіть повну адресу доставки'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Номер телефону'}),
            'payment_method': forms.Select(choices=[
                ('card', 'Банківська карта'),
                ('paypal', 'PayPal'),
                ('cash_on_delivery', 'Оплата при отриманні'),
            ])
        }

class SharedOrderForm(forms.ModelForm):
    class Meta:
        model = SharedOrder
        fields = ['region', 'city', 'street', 'building', 'phone', 'payment_method']
        widgets = {
            'region': forms.TextInput(attrs={'placeholder': 'Область'}),
            'city': forms.TextInput(attrs={'placeholder': 'Місто'}),
            'street': forms.TextInput(attrs={'placeholder': 'Вулиця'}),
            'building': forms.TextInput(attrs={'placeholder': 'Номер будинку'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Номер телефону'}),
            'payment_method': forms.Select()
        }

class SharedOrderContributionForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    payment_method = forms.ChoiceField(choices=[
        ('balance', 'З балансу'),
        ('card', 'Картка'),
    ])

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['reason', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Опишіть причину скарги...'}),
        }
