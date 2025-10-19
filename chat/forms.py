from django import forms
from .models import SupportSession, SupportMessage
class SupportSessionForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Коротко опишіть проблему'
        }),
        label='Тема звернення'
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Опишіть вашу проблему детально. Чим більше інформації ви надасте, тим швидше ми зможемо вам допомогти.',
            'rows': 5,
            'maxlength': '1000'
        }),
        label='Детальний опис',
        required=True
    )

    class Meta:
        model = SupportSession
        fields = ['subject']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError("Детальний опис не може бути порожнім")
        return content.strip()


class SupportMessageForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'message-input',
                'placeholder': 'Напишіть ваше повідомлення...',
                'rows': 1,
                'required': True
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError("Повідомлення не може бути порожнім")
        return content.strip()