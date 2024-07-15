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
    Recommendation, Pin, Notification, Report, FAQ)
from .serializers import (
    ArticleListSerializer, ArticleCreateSerializer,
    ArticleDetailSerializer, TopicFollowSerializer, CommentSerializer,
    FavoriteSerializer, ClapSerializer, DefaultResponseSerializer,
    ReadingHistorySerializer, RecommendationSerializer, AuthorFollowSerializer,
    NotificationSerializer, NotificationUpdateSerializer, ReportSerializer,
    FAQSerializer)
from users.serializers import ValidationErrorSerializer, UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ArticleFilter, SearchFilter
from rest_framework.decorators import action

User = get_user_model()


@extend_schema_view(
    create=extend_schema(
        summary="Create an article",
        request=ArticleCreateSerializer,
        responses={
            201: ArticleCreateSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        }
    ),
    list=extend_schema(
        summary="List articles",
        responses={
            200: ArticleListSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve an article",
        request=None,
        responses={
            200: ArticleDetailSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        }
    ),
    partial_update=extend_schema(
        summary="Update an article",
        request=ArticleCreateSerializer,
        responses={
            200: ArticleDetailSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        }
    ),
    destroy=extend_schema(
        summary="Delete an article",
        responses={
            204: None,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        }
    )
)
class ArticlesView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ArticleFilter
    filter_backends = [DjangoFilterBackend]
    parser_classes = [parsers.MultiPartParser]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return ArticleCreateSerializer
        if self.action == 'list':
            return ArticleListSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Article.objects.none()

        user = self.request.user
        queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)

        if user.is_authenticated:
            recommendations = Recommendation.objects.filter(user=user)
            more_topics = recommendations.values_list('more', flat=True)
            less_topics = recommendations.values_list('less', flat=True)

            if more_topics.exists():
                queryset = queryset.filter(topics__in=more_topics)
            if less_topics.exists():
                queryset = queryset.exclude(topics__in=less_topics)

        return queryset.distinct()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        ReadingHistory.objects.get_or_create(
            user=request.user, article=instance
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        summary="Archive an article",
        description="Set the status of the article to 'archive'.",
        responses={
            200: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        },
        tags=['articles']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def archive(self, request, pk=None):
        article = self.get_object()
        article.status = ArticleStatus.ARCHIVE
        article.save(update_fields=['status'])
        return Response({"detail": _("Maqola arxivlandi.")}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Pin an article",
        description="Pin an article for the authenticated user.",
        responses={
            200: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        },
        tags=['articles']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pin(self, request, pk=None):
        article = self.get_object()
        user = request.user

        if Pin.objects.filter(user=user, article=article).exists():
            return Response({"status": _("Maqola allaqachon pin qilingan.")}, status=status.HTTP_400_BAD_REQUEST)

        Pin.objects.create(user=user, article=article)
        return Response({"status": _("Maqola pin qilindi.")}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Unpin an article",
        description="Unpin an article for the authenticated user.",
        responses={
            200: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            400: DefaultResponseSerializer
        },
        tags=['articles']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unpin(self, request, pk=None):
        article = self.get_object()
        user = request.user

        pin = Pin.objects.filter(user=user, article=article).first()
        if not pin:
            return Response({"status": _("Maqola pin qilinmagan")}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get user-pinned articles",
    description="Retrieve a list of articles pinned by the authenticated user.",
    request=None,
    responses={
        200: ArticleListSerializer(many=True),
        404: DefaultResponseSerializer,
        400: DefaultResponseSerializer
    }
)
class UserPinnedArticles(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleListSerializer
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return Article.objects.filter(pins__user=user)


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
    patch=extend_schema(
        summary="Follow or unfollow a author",
        request=AuthorFollowSerializer,
        responses={
            201: DefaultResponseSerializer,
            204: DefaultResponseSerializer,
            400: ValidationErrorSerializer,
            404: ValidationErrorSerializer
        }
    )
)
class AuthorFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuthorFollowSerializer

    def create_notification(self, user, message):
        Notification.objects.create(user=user, message=message)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            follower = request.user
            author_id = serializer.validated_data['author_id']
            followee = get_object_or_404(User, id=author_id)

            try:
                follow = Follow.objects.get(
                    follower=follower, followee=followee)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                Follow.objects.create(follower=follower, followee=followee)

                message_followee = _("{} sizga follow qildi.").format(
                    follower.username)
                self.create_notification(followee, message_followee)

                return Response(status=status.HTTP_201_CREATED)

        raise exceptions.ValidationError(serializer.errors)


@extend_schema_view(
    create=extend_schema(
        summary="Create a comment",
        request=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    ),
    partial_update=extend_schema(
        summary="Update comment",
        request=CommentSerializer,
        responses={
            200: CommentSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    ),
    destroy=extend_schema(
        summary="Delete comment",
        request=None,
        responses={
            204: None,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer}
    )
)
class CommentView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'patch', 'delete']


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
        request=None,
        responses={
            201: DefaultResponseSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer}
    ),
    delete=extend_schema(
        summary="Delete Favorite",
        request=None,
        responses={
            204: None,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
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
            return Response({'detail': _("Maqola allaqachon sevimlilar ro'yxatiga kiritilgan.")}, status=status.HTTP_400_BAD_REQUEST)

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
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    ),
    delete=extend_schema(
        summary="Undo Claps",
        request=None,
        responses={
            204: None,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
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
            200: DefaultResponseSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
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
        request=RecommendationSerializer,
        responses={
            201: DefaultResponseSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    )
)
class RecommendationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecommendationSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            more_topic_id = serializer.validated_data.get('more_topic_id')
            less_topic_id = serializer.validated_data.get('less_topic_id')

            more_topic = None
            if more_topic_id:
                more_topic = get_object_or_404(
                    Topic, id=more_topic_id, is_active=True)
            less_topic = None
            if less_topic_id:
                less_topic = get_object_or_404(
                    Topic, id=less_topic_id, is_active=True)

            Recommendation.objects.create(
                user=user, more=more_topic, less=less_topic)
            return Response({"detail": _("Ajoyib, shunga o'xshash ko'proq maqolalarni tavsiya qilamiz.")}, status=status.HTTP_201_CREATED)

        raise exceptions.ValidationError(serializer.errors)


@extend_schema_view(
    list=extend_schema(
        summary="Get user notifications",
        request=None,
        responses={
            200: NotificationSerializer(many=True),
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve a notification",
        request=None,
        responses={
            200: NotificationSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    ),
    partial_update=extend_schema(
        summary="Update user notifications",
        request=NotificationUpdateSerializer,
        responses={
            200: DefaultResponseSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    )
)
class UserNotificationView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, read_at__isnull=True)


@extend_schema_view(
    post=extend_schema(
        summary="Report topic",
        request=ReportSerializer,
        responses={
            201: DefaultResponseSerializer,
            200: DefaultResponseSerializer,
            400: DefaultResponseSerializer,
            404: DefaultResponseSerializer,
            401: DefaultResponseSerializer
        }
    )
)
class ReportTopicView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            topic_id = serializer.validated_data['topic'].id
            topic = get_object_or_404(Topic, id=topic_id, is_active=True)

            report, created = Report.objects.get_or_create(
                user=user, topic=topic)

            if created:
                return Response({"status": _("Mavzu muvaffaqiyatli xabar qilindi.")}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": _("Mavzu allaqachon xabar qilingan.")}, status=status.HTTP_200_OK)

        raise exceptions.ValidationError(serializer.errors)


@extend_schema_view(
    get=extend_schema(
        summary="FAQs",
        request=None,
        responses={
            200: FAQSerializer,
            400: DefaultResponseSerializer
        }
    )
)
class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]
