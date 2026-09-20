from django import forms
from django.contrib.auth.models import User
from .models import Profile

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["first_name","username","email"]
    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data.get("username")).exists():
            raise forms.ValidationError("Username already exists.")
        return data
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Profile.objects.create(user=user, role="student")
        return user
