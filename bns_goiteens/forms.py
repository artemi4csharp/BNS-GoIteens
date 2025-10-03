from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']

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