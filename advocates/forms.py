from django import forms
from django.utils.text import slugify
from .models import ContactMessage, ScheduledCall, Article
from .models import LEGAL_SERVICES, Category

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "phone_number", "email", "subject", "message"]


class ScheduledCallForm(forms.ModelForm):
    class Meta:
        model = ScheduledCall
        fields = ["first_name", "last_name", "email", "phone_number", "subject", "date", "time_slot"]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "category", "author", "content", "image"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 shadow-sm px-4 py-3 placeholder-gray-400 text-gray-800",
                "placeholder": "Enter blog title"
            }),
            "category": forms.Select(attrs={
                "class": "w-full rounded-lg border-gray-300 shadow-sm focus:border-amber-500 focus:ring focus:ring-amber-200"
            }),
            "author": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 shadow-sm px-4 py-3 text-gray-800",
                "placeholder": "Author name"
            }),
            "content": forms.Textarea(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 shadow-sm px-4 py-3 placeholder-gray-400 text-gray-800",
                "rows": 10,
                "placeholder": "Write your article here..."
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-amber-100 file:text-amber-700 hover:file:bg-amber-200"
            }),
        }