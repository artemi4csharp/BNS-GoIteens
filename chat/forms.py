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
                'class': 'form-control',
                'placeholder': 'Введіть повідомлення...',
                'rows': 3
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError("Повідомлення не може бути порожнім")
        return content.strip()
