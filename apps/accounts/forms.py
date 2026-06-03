from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter last name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter email address'}))
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter phone number'}))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'placeholder': 'Street address, Apartment, Suite, etc.', 'rows': 3}))
    city = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'State/Province'}))
    zip_code = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'ZIP/Postal Code'}))

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "phone_number", "address", "city", "state", "zip_code")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
