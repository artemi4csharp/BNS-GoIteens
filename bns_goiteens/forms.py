from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, PromoCode

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
