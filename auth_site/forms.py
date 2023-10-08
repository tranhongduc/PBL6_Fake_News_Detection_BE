from django import forms
from .models import Account
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput, 
        label='username',
        error_messages={
            'required': 'Tên người dùng không được để trống',
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput, 
        label='email',
        error_messages={
            'required': 'Email không được để trống',
            'invalid': 'Định dạng email không hợp lệ',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='password',
        error_messages={
            'required': 'Mật khẩu không được để trống',
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, 
        label='confirm_password',
        error_messages={
            'required': 'Mật khẩu xác nhận không được để trống',
        }
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise ValidationError("Email đã tồn tại")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Mật khẩu phải có ít nhất 8 ký tự")
        if len(password) > 15:
            raise ValidationError("Mật khẩu không được nhiều hơn 15 ký tự")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Mật khẩu xác nhận không khớp")
        if len(confirm_password) < 8:
            raise ValidationError("Mật khẩu xác nhận phải có ít nhất 8 ký tự")
        if len(confirm_password) > 15:
            raise ValidationError("Mật khẩu xác nhận không được nhiều hơn 15 ký tự")
        return confirm_password
    