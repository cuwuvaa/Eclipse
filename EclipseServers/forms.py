from django import forms
from .models import VoiceServer, ServerMember

class VoiceServerCreateForm(forms.ModelForm):
    """Форма создания сервера"""
    
    class Meta:
        model = VoiceServer
        fields = ['name', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название сервера'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание сервера',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'avatar-input'
            }),
        }
        labels = {
            'name': 'Название сервера',
            'bio': 'Описание сервера',
            'image':'Аватар сервера',
        }
    
    def clean_name(self):
        """Валидация названия сервера"""
        name = self.cleaned_data['name']
        if len(name.strip()) < 2:
            raise forms.ValidationError("Название сервера должно содержать минимум 2 символа")
        return name

class VoiceServerEditForm(forms.ModelForm):
    """Форма редактирования сервера"""
    
    class Meta:
        model = VoiceServer
        fields = ['name', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название сервера'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание сервера',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'avatar-input'
            }),
        }
        labels = {
            'name': 'Название сервера',
            'bio': 'Описание сервера',
            'image':'Аватар сервера,'
        }
    
    def clean_name(self):
        """Валидация названия сервера"""
        name = self.cleaned_data['name']
        if len(name.strip()) < 2:
            raise forms.ValidationError("Название сервера должно содержать минимум 2 символа")
        return name