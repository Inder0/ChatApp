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