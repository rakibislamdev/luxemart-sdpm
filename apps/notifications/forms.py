from django import forms

from .models import ContactSubmission


class ContactSubmissionForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "you@example.com"}),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control form-control-lg",
                    "rows": 6,
                    "placeholder": "Tell us what you need help with, a suggestion, or any issue you want to report.",
                }
            ),
        }