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
    user = UserSerializer(read_only=True)

    class Meta:
        model = Clap
        fields = ['user', 'article', 'count']


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count',
                  'created_at', 'updated_at', 'topics', 'comments_count', 'claps_count']


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topics = TopicSerializer(many=True)
    comments = CommentSerializer(many=True)
    claps = ClapSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count',
                  'created_at', 'updated_at', 'topics', 'comments', 'claps']


class ArticleCreateSerializer(serializers.ModelSerializer):
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.filter(is_active=True), many=True, write_only=True, source='topics'
    )

    class Meta:
        model = Article
        fields = ['author', 'title', 'summary', 'content', 'status', 'thumbnail', 'topic_ids']

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
