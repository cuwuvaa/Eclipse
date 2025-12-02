from django import forms
from EclipseRoom.models import room, roomuser

class RoomCreationForm(forms.ModelForm):
    name = forms.CharField(
        label='room name',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter a room name'
        })
    )
    description = forms.CharField(
        label='description',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Enter a description for your room'
        })
    )
    class Meta:
        model = room.Room
        fields = ['name', 'description']