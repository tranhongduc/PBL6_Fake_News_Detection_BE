from rest_framework import serializers
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from . import models
from .models import Account 
        
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = '__all__'

class AccountSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ['username', 'email', 'avatar']
    def validate_email(self, value):
        # Validate email format using EmailValidator
        email_validator = EmailValidator("Enter a valid email address.")
        try:
            email_validator(value)
        except ValidationError as e:
            raise serializers.ValidationError({"email": e.messages})
        if Account.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The new password must have at least 8 characters")
        if len(value) > 15:
            raise serializers.ValidationError("New password must not be more than 15 characters")
    def validate_confirm_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The confirm new password must have at least 8 characters")
        if len(value) > 15:
            raise serializers.ValidationError("Confirm new password must not be more than 15 characters")
    def validate(self, value):
        new_password = value.get('new_password')
        confirm_new_password = value.get('confirm_new_password')
        old_password = value.get('old_password')
        if new_password and old_password and new_password == old_password:
            raise serializers.ValidationError("The new password duplicates the old password.")
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise serializers.ValidationError("New passwords do not match.")
        return value
  