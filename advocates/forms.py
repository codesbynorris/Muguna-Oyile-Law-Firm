from django import forms
from .models import ContactMessage, ScheduledCall

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "phone_number", "email", "subject", "message"]


class ScheduledCallForm(forms.ModelForm):
    class Meta:
        model = ScheduledCall
        fields = ["first_name", "last_name", "email", "phone_number", "subject", "date", "time_slot"]
