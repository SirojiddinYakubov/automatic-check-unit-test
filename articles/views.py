from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, parsers, generics, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import (
    Topic, Article, TopicFollow, ArticleStatus,
    Comment, Favorite, Clap, ReadingHistory, Follow,
    Recommendation)
from .serializers import (
    ArticleListSerializer, ArticleCreateSerializer,
    ArticleDetailSerializer,
    TopicFollowSerializer, CommentSerializer,
    FavoriteSerializer, ClapSerializer, DefaultResponseSerializer,
    ReadingHistorySerializer, FollowRequestSerializer, FollowResponseSerializer,
    RecommendationRequestSerializer, RecommendationResponseSerializer)
from users.serializers import ValidationErrorSerializer, UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ArticleFilter, SearchFilter

User = get_user_model()


@extend_schema_view(
    create=extend_schema(
        summary="Create an article",
        request=ArticleCreateSerializer,
        responses={201: ArticleListSerializer, 400: "Bad Request"}
    ),
    list=extend_schema(
        operation_id="list_articles",
        summary="List articles",
        responses={200: ArticleListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Retrieve an article",
        responses={200: ArticleDetailSerializer}
    ),
    partial_update=extend_schema(
        summary="Partial update article",
        request=ArticleCreateSerializer,
        responses={200: ArticleListSerializer}
    ),
    destroy=extend_schema(
        summary="Delete an article",
        responses={204: "No Content"}
    )
)
class ArticlesView(viewsets.ModelViewSet):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ArticleFilter
    queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)
    filter_backends = [DjangoFilterBackend]
    parser_classes = [parsers.MultiPartParser]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        ReadingHistory.objects.get_or_create(
            user=request.user, article=instance
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema_view(
    patch=extend_schema(
        summary="Follow or unfollow a topic",
        request=TopicFollowSerializer,
        responses={
            201: DefaultResponseSerializer,
            200: DefaultResponseSerializer,
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

            topic_follow, created = TopicFollow.objects.get_or_create(
                user=user, topic=topic)

            if created:
                return Response({"detail": _("Siz '{topic_name}' mavzusini kuzatyapsiz.".format(topic_name=topic.name))}, status=status.HTTP_201_CREATED)
            else:
                topic_follow.delete()
                return Response({"detail": _("Siz '{topic_name}' mavzusini kuzatishni bekor qildingiz.".format(topic_name=topic.name))}, status=status.HTTP_200_OK)

        raise exceptions.ValidationError(serializer.errors)


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


@extend_schema_view(
    get=extend_schema(
        summary="Search",
        request=ArticleListSerializer,
        responses={200: ArticleListSerializer}
    ))
class SearchView(generics.ListAPIView):
    queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)
    serializer_class = ArticleListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SearchFilter


@extend_schema_view(
    post=extend_schema(
        summary="Add Article To Favorite",
        request=ArticleListSerializer,
        responses={200: DefaultResponseSerializer}
    ),
    delete=extend_schema(
        summary="Delete Favorite",
        request=ArticleListSerializer
    ))
class FavoriteArticleView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)
    serializer_class = ArticleListSerializer

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, article=article)
        if created:
            return Response({'detail': _("Maqola sevimlilarga qo'shildi.")}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': _("Maqola allaqachon sevimlilar ro'yxatiga kiritilgan.")}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        favorite = get_object_or_404(
            Favorite, user=request.user, article=article)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="User Favorites",
        request=None,
        responses={200: ArticleListSerializer}
    ))
class UserFavoritesListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)


@extend_schema_view(
    post=extend_schema(
        summary="Clap To Article",
        request=None,
        responses={
            201: ClapSerializer,
            401: ValidationErrorSerializer
        }
    ),
    delete=extend_schema(
        summary="Undo Claps",
        request=None,
        responses={
            200: DefaultResponseSerializer,
            400: ValidationErrorSerializer,
            404: ValidationErrorSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ClapView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClapSerializer

    def get_queryset(self):
        return Article.objects.filter(status=ArticleStatus.PUBLISH)

    def post(self, request, article_id):
        user = request.user
        article = get_object_or_404(self.get_queryset(), id=article_id)

        clap, created = Clap.objects.get_or_create(user=user, article=article)
        clap.count = min(clap.count + 1, 50)
        clap.save()

        response_serializer = self.serializer_class(clap)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, article_id):
        user = request.user
        article = get_object_or_404(self.get_queryset(), id=article_id)

        try:
            clap = Clap.objects.get(user=user, article=article)
            clap.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Clap.DoesNotExist:
            raise exceptions.NotAcceptable


@extend_schema_view(
    post=extend_schema(
        summary="Article Reads",
        request=None,
        responses={
            202: DefaultResponseSerializer,
            404: ValidationErrorSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ArticleReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        try:
            instance = Article.objects.get(id=article_id)
            instance.reads_count += 1
            instance.save(update_fields=['reads_count'])
            return Response({"detail": _("Maqolani o'qish soni ortdi.")}, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            raise exceptions.NotFound


@extend_schema_view(
    get=extend_schema(
        summary="Popular Authors",
        request=None,
        responses={
            200: UserSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class PopularAuthorsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            is_active=True,
            article__status=ArticleStatus.PUBLISH
        ).annotate(
            total_reads_count=Sum('article__reads_count')
        ).order_by('-total_reads_count')[:5]


@extend_schema_view(
    get=extend_schema(
        summary="Reading History",
        request=None,
        responses={
            200: ArticleListSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ReadingHistoryView(generics.ListAPIView):
    serializer_class = ReadingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReadingHistory.objects.filter(user=self.request.user).order_by('-created_at')


@extend_schema_view(
    post=extend_schema(
        summary="Follow an Author",
        request=FollowRequestSerializer,
        responses={201: FollowResponseSerializer}
    )
)
class FollowView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowRequestSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            follower = request.user
            followee_id = serializer.validated_data['followee_id']

            followee = get_object_or_404(self.get_queryset(), id=followee_id)

            if Follow.objects.filter(follower=follower, followee=followee).exists():
                return Response({"detail": _("Siz allaqachon bu foydalanuvchini kuzatib borasiz.")}, status=status.HTTP_400_BAD_REQUEST)

            follow = Follow.objects.create(
                follower=follower, followee=followee)
            response_serializer = FollowResponseSerializer(follow)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        raise exceptions.ValidationError(serializer.errors)


@extend_schema_view(
    delete=extend_schema(
        summary="Unfollow an Author",
        responses={
            204: None,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer
        }
    )
)
class UnfollowView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def get_object(self):
        return generics.get_object_or_404(self.get_queryset(), id=self.kwargs['followee_id'])

    def delete(self, request, followee_id, *args, **kwargs):
        follower = request.user

        followee = self.get_object()

        try:
            follow = Follow.objects.get(follower=follower, followee=followee)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            raise exceptions.NotFound


@extend_schema_view(
    get=extend_schema(
        summary="Followers List",
        request=None,
        responses={
            200: UserSerializer,
        }
    )
)
class FollowersListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return User.objects.filter(following__followee_id=user_id, is_active=True)


@extend_schema_view(
    get=extend_schema(
        summary="Following List",
        request=None,
        responses={
            200: UserSerializer
        }
    )
)
class FollowingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return User.objects.filter(followers__follower_id=user_id, is_active=True)


@extend_schema_view(
    post=extend_schema(
        summary="Recommend More Articles",
        request=RecommendationRequestSerializer,
        responses={201: RecommendationResponseSerializer}
    )
)
class RecommendationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecommendationRequestSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            more_topic_id = serializer.validated_data['more_topic_id']
            less_topic_id = serializer.validated_data.get('less_topic_id')

            more_topic = get_object_or_404(
                Topic, id=more_topic_id, is_active=True)
            less_topic = None
            if less_topic_id:
                less_topic = get_object_or_404(
                    Topic, id=less_topic_id, is_active=True)

            recommendation = Recommendation.objects.create(
                user=user, more=more_topic, less=less_topic)
            response_serializer = RecommendationResponseSerializer(
                recommendation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        raise exceptions.ValidationError(serializer.errors)


@extend_schema_view(
    post=extend_schema(
        summary="User Recommendations",
        request=None,
        responses={201: RecommendationResponseSerializer}
    )
)
class UserRecommendationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecommendationResponseSerializer

    def get_queryset(self):
        user = self.request.user
        return Recommendation.objects.filter(user=user)
