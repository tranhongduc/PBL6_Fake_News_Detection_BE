from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from . import models
        
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = '__all__'