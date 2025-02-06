from django import forms
from .models import Comment , Profile ,Post
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from ckeditor.widgets import CKEditorWidget


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='Required.',
        widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='Required.',
        widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        max_length=254, 
        help_text='Required.',
        widget=forms.EmailInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Email Address'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Confirm Password'}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Password'})
    )
    
    
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-input mt-1 block w-full', 'multiple': False}),
        }
        
        
class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'image']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#e87a00]',
            }),
        }