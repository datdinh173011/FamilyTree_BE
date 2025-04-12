from rest_framework import serializers
from .models import NewsCategory, NewsArticle, NewsComment
from account.serializers import UserSerializer

class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = '__all__'


class NewsCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = NewsComment
        fields = ['id', 'article', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user']


class NewsArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'content', 'category', 'category_name', 'author', 'image', 
                 'created_at', 'updated_at', 'published_at', 'is_published', 'view_count', 'comments_count']
        read_only_fields = ['author', 'view_count']
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class NewsArticleDetailSerializer(NewsArticleSerializer):
    comments = NewsCommentSerializer(many=True, read_only=True)
    
    class Meta(NewsArticleSerializer.Meta):
        fields = NewsArticleSerializer.Meta.fields + ['comments']
