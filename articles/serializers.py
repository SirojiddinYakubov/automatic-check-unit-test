from rest_framework import serializers
from .models import Topic, Article, Comment, Clap
from users.serializers import UserSerializer


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['article', 'user', 'parent', 'content']


class ClapSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Clap
        fields = ['user', 'article', 'count']


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    topics = TopicSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'thumbnail', 'views_count',
                  'formatted_created_at', 'formatted_updated_at', 'topics', 'comments_count', 'claps_count']


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    topics = TopicSerializer(many=True)
    comments = CommentSerializer(many=True)
    claps = ClapSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'thumbnail', 'views_count',
                  'formatted_created_at', 'formatted_updated_at', 'topics', 'comments', 'claps']


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['topics', 'title', 'summary', 'content', 'thumbnail']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['topics', 'title', 'summary', 'content', 'thumbnail']


class ArticleDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id']


class TopicFollowSerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()
