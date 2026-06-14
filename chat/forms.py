from django.forms import ModelForm
from django import forms
from .models import ChatGroup,Message

class ChatMessageForm(ModelForm):
    class Meta:
        model=Message
        fields=['body']
        widgets={
            'body':forms.TextInput(attrs={'class': 'form-input','placeholder':'Type Message...','autofocus':True})
        }
        labels={
            'body':'',
        }

class GroupChatForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['title','is_protected','password']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Group Name',
                'autofocus': True
            }),
            'is_protected': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),

            'password': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Password'
            })
        }
        labels = {
            'title': '',
            'password': '',
        }
