from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Topic, Article, TopicFollow, ArticleStatus, Comment
from .serializers import (
    ArticleListSerializer, ArticleCreateSerializer,
    ArticleDeleteSerializer, ArticleDetailSerializer,
    TopicSerializer, TopicFollowSerializer, CommentSerializer)
from users.serializers import ValidationErrorSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ArticleFilter, TopicFilter

User = get_user_model()


@extend_schema_view(
    create=extend_schema(
        summary="Create an article",
        request=ArticleCreateSerializer,
        responses={200: ArticleListSerializer, 401: ValidationErrorSerializer}
    ),
    list=extend_schema(
        summary="List articles",
        responses={200: ArticleListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Article detail",
        responses={200: ArticleDetailSerializer(many=True)}
    ),
    update=extend_schema(
        summary="Update article",
        request=ArticleCreateSerializer,
        responses={200: ArticleListSerializer(many=True)}
    ),
    partial_update=extend_schema(
        summary="Partial update article",
        request=ArticleCreateSerializer,
        responses={200: ArticleListSerializer(many=True)}
    ),
    destroy=extend_schema(
        summary="Delete article",
        request=ArticleDeleteSerializer
    )
)
class ArticlesView(viewsets.ModelViewSet):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ArticleFilter
    queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)
    filter_backends = [DjangoFilterBackend]
    parser_classes = [parsers.MultiPartParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateSerializer
        if self.action == 'list':
            return ArticleListSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        if self.action == 'destroy':
            return ArticleDeleteSerializer


@extend_schema_view(
    create=extend_schema(
        summary="Create a topic",
        request=TopicSerializer,
        responses={200: TopicSerializer}
    ),
    list=extend_schema(
        summary="List topics",
        responses={200: TopicSerializer}
    ),
    retrieve=extend_schema(
        summary="Topic detail",
        request=TopicSerializer,
        responses={200: TopicSerializer}
    ),
    update=extend_schema(
        summary="Update topic",
        request=TopicSerializer,
        responses={200: TopicSerializer}
    ),
    partial_update=extend_schema(
        summary="Partial update topic",
        request=TopicSerializer,
        responses={200: TopicSerializer}
    ),
    destroy=extend_schema(
        summary="Delete topic",
        request=TopicSerializer
    )
)
class TopicsView(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TopicFilter
    queryset = Topic.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]


@extend_schema_view(
    patch=extend_schema(
        summary="Follow or unfollow a topic",
        request=TopicFollowSerializer,
        responses={
            201: {"detail": "You are now following topic."},
            200: {"detail": "You have unfollowed topic."},
            400: ValidationErrorSerializer,
            404: ValidationErrorSerializer
        }
    )
)
class TopicFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TopicFollowSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            topic_id = serializer.validated_data['topic_id']

            topic = get_object_or_404(Topic, id=topic_id, is_active=True)

            topic_follow, created = TopicFollow.objects.get_or_create(user=user, topic=topic)

            if created:
                return Response({"detail": f"You are now following topic '{topic.name}'."}, status=status.HTTP_201_CREATED)
            else:
                topic_follow.delete()
                return Response({"detail": f"You have unfollowed topic '{topic.name}'."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    create=extend_schema(
        summary="Create a comment",
        request=CommentSerializer,
        responses={200: CommentSerializer}
    ),
    list=extend_schema(
        summary="List comments",
        responses={200: CommentSerializer}
    ),
    retrieve=extend_schema(
        summary="comment detail",
        request=CommentSerializer,
        responses={200: CommentSerializer}
    ),
    update=extend_schema(
        summary="Update comment",
        request=CommentSerializer,
        responses={200: CommentSerializer}
    ),
    partial_update=extend_schema(
        summary="Partial update comment",
        request=CommentSerializer,
        responses={200: CommentSerializer}
    ),
    destroy=extend_schema(
        summary="Delete comment",
        request=CommentSerializer
    )
)
class CommentCreateView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
