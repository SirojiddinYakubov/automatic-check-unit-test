from rest_framework import serializers
from .models import (
    Topic, Article, Comment, Clap, Favorite, ReadingHistory,
    Follow, Recommendation, Pin)
from users.serializers import UserSerializer
from drf_spectacular.utils import extend_schema_field
from django.db.models import Sum
from django.contrib.auth import get_user_model

User = get_user_model()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']


class CommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['article', 'user', 'parent', 'content']


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
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.filter(is_active=True), many=True, write_only=True, source='topics'
    )

    class Meta:
        model = Article
        fields = ['author', 'title', 'summary',
                  'content', 'thumbnail', 'topic_ids']

    def create(self, validated_data):
        topics = validated_data.pop('topics', [])
        article = Article.objects.create(**validated_data)
        article.topics.set(topics)
        return article

    def update(self, instance, validated_data):
        topics = validated_data.pop('topics', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if topics is not None:
            instance.topics.set(topics)
        instance.save()
        return instance


class ArticleDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id']


class TopicFollowSerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()


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


class FollowRequestSerializer(serializers.Serializer):
    followee_id = serializers.IntegerField()


class FollowResponseSerializer(serializers.ModelSerializer):
    follower = UserSerializer
    followee = UserSerializer

    class Meta:
        model = Follow
        fields = ['follower', 'followee', 'created_at']


class RecommendationRequestSerializer(serializers.Serializer):
    more_topic_id = serializers.IntegerField(required=True)
    less_topic_id = serializers.IntegerField(required=False)


class RecommendationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['user', 'more', 'less', 'created_at']


class PinRequestSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()


class PinResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pin
        fields = ['id', 'user', 'article', 'created_at']
