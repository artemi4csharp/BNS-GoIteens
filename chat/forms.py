from django import forms
from .models import SupportSession, SupportMessage

class SupportSessionForm(forms.ModelForm):
    class Meta:
        model = SupportSession
        fields = ['subject']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема звернення'
            })
        }


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


class SupportSessionForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Коротко опишіть проблему'
        })
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Опишіть вашу проблему детально. Чим більше інформації ви надасте, тим швидше ми зможемо вам допомогти.',
            'maxlength': '1000'
        })
    )

    class Meta:
        model = SupportSession
        fields = ['subject']