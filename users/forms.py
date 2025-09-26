# users/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Save profile
            profile = UserProfile(user=user, profile_picture=self.cleaned_data['profile_picture'])
            profile.save()
        return user
