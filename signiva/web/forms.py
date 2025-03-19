from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Document, Profile, DocumentSignature

class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information.
    """
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = Profile
        fields = []

class DocumentForm(forms.ModelForm):
    """
    Form for creating and updating documents.
    """
    class Meta:
        model = Document
        fields = ['title', 'file']

class SignatureRequestForm(forms.Form):
    """
    Form for requesting document signatures.
    
    Fields:
        signer_email: Email address of the person who needs to sign
    """
    signer_email = forms.EmailField(
        label='Signer Email',
        help_text='Enter the email address of the person who needs to sign the document.',
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'signer@example.com'
        })
    )