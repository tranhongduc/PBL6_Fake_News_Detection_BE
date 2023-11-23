from rest_framework import serializers
from .models import Categories, News, Comments
        
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

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'