from rest_framework import serializers
from .models import Categories, News, Comments
        
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'image', 'label', 'account_id', 'category_id', 'created_at', 'updated_at']

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'text', 'account_id', 'news_id', 'created_at', 'updated_at']