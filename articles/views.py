from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Topic, Article, TopicFollow
from .serializers import (
    ArticleListSerializer, ArticleCreateSerializer,
    ArticleDeleteSerializer, ArticleUpdateSerializer,
    ArticleDetailSerializer,
    TopicSerializer, TopicFollowSerializer,)
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
        request=ArticleUpdateSerializer,
        responses={200: ArticleListSerializer(many=True)}
    ),
    partial_update=extend_schema(
        summary="Partial update article",
        request=ArticleUpdateSerializer,
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
    queryset = Article.objects.filter(status="publish")
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        if self.action == 'list':
            return ArticleListSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        if self.action == 'update':
            return ArticleUpdateSerializer
        if self.action == 'partial_update':
            return ArticleUpdateSerializer
        if self.action == 'destroy':
            return ArticleDeleteSerializer


@extend_schema_view(
    create=extend_schema(
        summary="Create an topic",
        request=TopicSerializer,
        responses={200: TopicSerializer}
    ),
    list=extend_schema(
        summary="List topices",
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

            try:
                topic = Topic.objects.get(id=topic_id, is_active=True)
            except Topic.DoesNotExist:
                return Response({"detail": "Topic does not exist."}, status=status.HTTP_404_NOT_FOUND)

            if topic:
                if not TopicFollow.objects.filter(user=user, topic=topic).exists():
                    TopicFollow.objects.create(user=user, topic=topic)
                    return Response({"detail": f"You are now following topic '{topic.name}'."},
                                    status=status.HTTP_201_CREATED)
                else:
                    topic_follow = TopicFollow.objects.get(
                        user=user, topic=topic)
                    topic_follow.delete()
                    return Response({"detail": f"You have unfollowed topic '{topic.name}'."},
                                    status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
