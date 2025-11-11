from django import forms
from django.utils.text import slugify
from .models import ContactMessage, Profile, Quote, ScheduledCall, Article
from .models import LEGAL_SERVICES, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "phone_number", "email", "subject", "message"]


class ScheduledCallForm(forms.ModelForm):
    class Meta:
        model = ScheduledCall
        fields = ["first_name", "last_name", "email", "phone_number", "subject", "date", "time_slot"]

class ArticleForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=[
            ('publication', 'Publication'),
            ('article', 'Article'),
            ('news', 'News'),
            ('quote', 'Quote'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 text-gray-700 font-content invalid:border-red-500 invalid:ring-red-500',
            'style': 'font-family: "Open Sans", sans-serif;'
        })
    )

    class Meta:
        model = Article
        fields = ['title', 'category', 'author', 'content', 'image', 'type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full text-3xl font-bold text-gray-900 border-0 p-0 focus:ring-0 focus:border-indigo-500 pb-2 transition placeholder-gray-300 font-content invalid:border-red-500 invalid:ring-red-500',
                'placeholder': 'Enter a concise, SEO-friendly headline',
                'style': 'font-family: "Open Sans", sans-serif;'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 text-gray-700 font-content invalid:border-red-500 invalid:ring-red-500',
                'style': 'font-family: "Open Sans", sans-serif;'
            }),
            'author': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 text-gray-700 font-content invalid:border-red-500 invalid:ring-red-500',
                'placeholder': 'Select or enter author name',
                'style': 'font-family: "Open Sans", sans-serif;'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-gray-200 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 text-gray-700 font-content invalid:border-red-500 invalid:ring-red-500',
                'rows': 22,
                'placeholder': 'Start writing your professional article here...',
                'style': 'font-family: "Open Sans", sans-serif;'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-3 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 transition duration-150',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['image'].required = False
        self.fields['title'].required = False  # Validated in clean()
        self.fields['category'].required = False  # Validated in clean()
        self.fields['author'].required = True
        self.fields['content'].required = True
        self.fields['type'].required = True

    def clean(self):
        cleaned_data = super().clean()
        type = cleaned_data.get('type')
        if type == 'publication':
            if not cleaned_data.get('title'):
                self.add_error('title', 'Title is required for publications.')
            if not cleaned_data.get('category'):
                self.add_error('category', 'Category is required for publications.')
        elif type in ('article', 'news'):
            if not cleaned_data.get('title'):
                self.add_error('title', 'Title is required for articles and news.')
        return cleaned_data    

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(max_length=254, required=True, label="Email Address")
    avatar = forms.ImageField(required=False, label="Profile Picture")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'avatar']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create or update the Profile instance
            profile, created = Profile.objects.get_or_create(user=user)
            if self.cleaned_data['avatar']:
                profile.image = self.cleaned_data['avatar']
                profile.save()
        return user
    