from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'class': 'form-control'
        }),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'class': 'form-control'
        }),
        required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Phone Number (Optional)',
            'class': 'form-control'
        }),
        required=False
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'How can we help you?',
            'class': 'form-control',
            'rows': 5
        }),
        required=True
    )