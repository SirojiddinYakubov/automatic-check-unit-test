from rest_framework import serializers
from .models import (
    Topic, Article, Comment, Clap, Pin, Notification, Report, FAQ)
from users.serializers import UserSerializer
from drf_spectacular.utils import extend_schema_field
from django.db.models import Sum
from django.contrib.auth import get_user_model
from .models import ArticleStatus

User = get_user_model()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'parent', 'content', 'created_at', 'replies']
        read_only_fields = ['id', 'article', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'parent', 'content', 'created_at', 'replies']
        read_only_fields = ['id', 'article', 'user', 'parent', 'content', 'created_at', 'replies']


class ClapSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Clap
        fields = ['user', 'article', 'count']


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    claps_count = serializers.SerializerMethodField()

    @extend_schema_field(serializers.IntegerField)
    def get_comments_count(self, obj):
        return obj.comments.count()

    @extend_schema_field(serializers.IntegerField)
    def get_claps_count(self, obj):
        total_claps = obj.claps.aggregate(
            total_claps=Sum('count'))['total_claps']
        return total_claps if total_claps else 0

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count', 'reads_count',
                  'created_at', 'updated_at', 'topics', 'comments_count', 'claps_count']


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topics = TopicSerializer(many=True)
    claps = ClapSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count', 'reads_count',
                  'created_at', 'updated_at', 'topics', 'claps']


class ArticleDetailCommentsSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['comments']

    @extend_schema_field(serializers.CharField)
    def get_comments(self, obj: Article) -> list[dict]:
        comments = Comment.objects.filter(article=obj, parent=None)
        return CommentSerializer(comments, many=True).data


class ArticleCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.filter(is_active=True), many=True, write_only=True, required=True
    )
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content',
                  'status', 'thumbnail', 'topic_ids', 'topics', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        article = Article.objects.create(**validated_data, status=ArticleStatus.PENDING)
        article.topics.set(topic_ids)
        return article

    def update(self, instance, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.topics.set(topic_ids)
        instance.save()
        return instance


class DefaultResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class RecommendationSerializer(serializers.Serializer):
    more_article_id = serializers.IntegerField(required=False)
    less_article_id = serializers.IntegerField(required=False)


class PinRequestSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()


class PinResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pin
        fields = ['id', 'user', 'article', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'read_at', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['article']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer']
