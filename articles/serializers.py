from rest_framework import serializers
from .models import (
    Topic, Article, Comment, Clap, Favorite, ReadingHistory,
    Pin, Notification, Report, FAQ)
from users.serializers import UserSerializer
from drf_spectacular.utils import extend_schema_field
from django.db.models import Sum
from django.contrib.auth import get_user_model

User = get_user_model()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'parent',
                  'content', 'created_at', 'replies']

    @extend_schema_field(ReplySerializer(many=True))
    def get_replies(self, obj):
        if obj.parent is None:
            replies = Comment.objects.filter(parent=obj)
            return ReplySerializer(replies, many=True).data
        return []

    def create(self, validated_data):
        user = self.context['request'].user
        return Comment.objects.create(user=user, **validated_data)


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
    comments = CommentSerializer(many=True, read_only=True)
    claps = ClapSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count', 'reads_count',
                  'created_at', 'updated_at', 'topics', 'comments', 'claps']


class ArticleCreateSerializer(serializers.ModelSerializer):
    topic_ids = serializers.CharField(write_only=True)
    id = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content',
                  'status', 'thumbnail', 'topic_ids', 'created_at', 'updated_at']

    def validate_topic_ids(self, value):
        topic_ids = [int(tid.strip()) for tid in value.split(',')]

        existing_topic_ids = set(Topic.objects.values_list('pk', flat=True))
        invalid_ids = [
            tid for tid in topic_ids if tid not in existing_topic_ids]

        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid primary key(s): {
                    invalid_ids} - object does not exist."
            )
        return topic_ids

    def create(self, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        article = Article.objects.create(**validated_data)
        article.topics.set(topic_ids)
        return article

    def update(self, instance, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.topics.set(topic_ids)
        instance.save()
        return instance


class TopicFollowSerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()


class AuthorFollowSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()


class FavoriteSerializer(serializers.ModelSerializer):
    article = ArticleListSerializer()

    class Meta:
        model = Favorite
        fields = ['user', 'article', 'created_at']


class DefaultResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ReadingHistorySerializer(serializers.ModelSerializer):
    article = ArticleListSerializer(read_only=True)

    class Meta:
        model = ReadingHistory
        fields = ['id', 'article', 'created_at']


class RecommendationSerializer(serializers.Serializer):
    more_topic_id = serializers.IntegerField(required=False)
    less_topic_id = serializers.IntegerField(required=False)


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


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'read_at']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['topic']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer']
