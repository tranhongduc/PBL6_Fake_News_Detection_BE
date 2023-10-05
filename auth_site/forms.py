from django import forms
from .models import Account
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, max_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="confirm_password", max_length=8)
    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã tồn tại.")
        password = cleaned_data.get("password")
        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        print(password)
        confirm_password = cleaned_data.get("confirm_password")
        if len(confirm_password) < 8:
            raise forms.ValidationError("Mật khẩu xác nhận phải có ít nhất 8 ký tự.")
        print(confirm_password)
        if password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp.")
