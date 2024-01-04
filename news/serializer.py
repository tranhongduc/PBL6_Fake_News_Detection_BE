from rest_framework import serializers
from .models import Categories, News, Comments, Interacts
from auth_site import models
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

    def validate_text(self, value):
        if len(value) < 500:
            raise serializers.ValidationError("The 'text' field must have at least 500 characters.")
        return value

class NewsSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['title', 'text', 'image', 'label', 'category']
    def validate_text(self, value):
        if len(value) < 500:
            raise serializers.ValidationError("The 'text' field must have at least 500 characters.")
        return value
class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'

class CommentsSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['text']

class InteractsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interacts
        fields = '__all__'