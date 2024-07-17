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
    ArticleDetailSerializer, CommentSerializer,
    FavoriteSerializer, ClapSerializer, DefaultResponseSerializer,
    ReadingHistorySerializer, RecommendationSerializer,
    NotificationSerializer, ReportSerializer, FAQSerializer,
    ArticleDetailCommentsSerializer, CommentResponseSerializer)
from users.serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ArticleFilter, SearchFilter
from rest_framework.decorators import action
from django.utils import timezone
from django.db import models
from typing import Dict, Any

User = get_user_model()


def default_response(*args: Any) -> Dict[int, Any]:
    response_map = {}

    for arg in args:
        if isinstance(arg, tuple):
            status_code, serializer_class = arg
            response_map[status_code] = serializer_class
        elif isinstance(arg, int):
            response_map[arg] = DefaultResponseSerializer

    return response_map


@extend_schema_view(
    create=extend_schema(
        summary="Create an article",
        request=ArticleCreateSerializer,
        responses=default_response(
            (201, ArticleCreateSerializer), 400, 404
        )
    ),
    list=extend_schema(
        summary="List articles",
        responses=default_response(
            (200, ArticleListSerializer), 400, 404
        )
    ),
    retrieve=extend_schema(
        summary="Retrieve an article",
        request=None,
        responses=default_response(
            (200, ArticleDetailSerializer), 400, 404
        )
    ),
    partial_update=extend_schema(
        summary="Update an article",
        request=ArticleCreateSerializer,
        responses=default_response(
            (200, ArticleDetailSerializer), 400, 404
        )
    ),
    destroy=extend_schema(
        summary="Delete an article",
        responses=default_response(
            (204, None), 400, 403, 404
        )
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
        return None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Article.objects.none()

        user = self.request.user
        queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)

        if user.is_authenticated:
            recommendations = Recommendation.objects.filter(user=user)
            less_topics = recommendations.values_list('less', flat=True)

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user or request.user.is_superuser:
            instance.status = ArticleStatus.TRASH
            instance.save(update_fields=['status'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied()

    @extend_schema(
        summary="Archive an article",
        description="Set the status of the article to 'archive'.",
        responses=default_response(
            200, 400, 404
        ),
        tags=['articles']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def archive(self, request, pk=None):
        article = self.get_object()
        if article.author == request.user or request.user.is_superuser:
            article.status = ArticleStatus.ARCHIVE
            article.save(update_fields=['status'])
            return Response({"detail": _("Maqola arxivlandi.")}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Pin an article",
        description="Pin an article for the authenticated user.",
        responses=default_response(
            200, 400, 404
        ),
        tags=['articles']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pin(self, request, pk=None):
        article = self.get_object()
        user = request.user

        if Pin.objects.filter(user=user, article=article).exists():
            raise exceptions.ValidationError

        Pin.objects.create(user=user, article=article)
        return Response({"status": _("Maqola pin qilindi.")}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Unpin an article",
        description="Unpin an article for the authenticated user.",
        request=None,
        responses=default_response(
            (204, None), 400, 404
        ),
        tags=['articles']
    )
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unpin(self, request, pk=None):
        article = self.get_object()
        user = request.user

        pin = Pin.objects.filter(user=user, article=article).first()
        if not pin:
            raise exceptions.NotFound(_("Maqola topilmadi.."))

        pin.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Increment Article Reads Count",
        request=None,
        responses=default_response(
            200, 400, 401, 404
        ),
        tags=['articles']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def read(self, request, pk=None):
        article = self.get_object()

        try:
            article.reads_count += 1
            article.save(update_fields=['reads_count'])
            return Response({"detail": _("Maqolani o'qish soni ortdi.")}, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            raise exceptions.NotFound


@extend_schema(
    summary="Get user articles",
    description="Retrieve a list of articles pinned by the authenticated user.",
    request=None,
    responses=default_response(
            (200, ArticleListSerializer(many=True)), 400, 404
        )
)
class UserPinnedArticles(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleListSerializer
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user

        queryset = Article.objects.filter(author=user)
        pin_subquery = Pin.objects.filter(article=models.OuterRef('pk'), user=user)
        queryset = queryset.annotate(
            is_pinned=models.Exists(pin_subquery)
        )
        queryset = queryset.order_by('-is_pinned', '-created_at')
        return queryset


@extend_schema_view(
    post=extend_schema(
        summary="Follow a topic",
        request=None,
        responses=default_response(
            201, 200, 400, 404
        )
    ),
    delete=extend_schema(
        summary="Unfollow a topic",
        request=None,
        responses=default_response(
            200, (204, None), 400, 404
        )
    )
)
class TopicFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('id')
        user = request.user

        topic = get_object_or_404(Topic, id=topic_id, is_active=True)

        topic_follow, is_created = TopicFollow.objects.get_or_create(
            user=user, topic=topic)

        if is_created:
            return Response(
                {"detail": _("Siz '{topic_name}' mavzusini kuzatyapsiz.").format(topic_name=topic.name)},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"detail": _("Siz allaqachon '{topic_name}' mavzusini kuzatyapsiz.").format(topic_name=topic.name)},
                status=status.HTTP_200_OK
            )

    def delete(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('id')
        user = request.user

        topic = get_object_or_404(Topic, id=topic_id, is_active=True)

        try:
            topic_follow = TopicFollow.objects.get(user=user, topic=topic)
            topic_follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TopicFollow.DoesNotExist:
            return Response(
                {"detail": _("Siz '{topic_name}' mavzusini kuzatmaysiz.").format(topic_name=topic.name)},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    post=extend_schema(
        summary="Follow a author",
        request=None,
        responses=default_response(
         201, 200, 400, 404
        )
    ),
    delete=extend_schema(
        summary="Unfollow a author",
        request=None,
        responses=default_response(
        (204, None), 400, 404
        )
        )
)
class AuthorFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def create_notification(self, user, message):
        Notification.objects.create(user=user, message=message)

    def post(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')

        follower = request.user
        followee = get_object_or_404(User, id=author_id)

        try:
            follow, is_created = Follow.objects.get_or_create(follower=follower, followee=followee)
            if is_created:
                message_followee = _("{} sizga follow qildi.").format(follower.username)
                self.create_notification(followee, message_followee)
                return Response({'detail': _("Mofaqqiyatli follow qilindi.")}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': _("Siz allaqachon ushbu foydalanuvchini kuzatyapsiz.")},
                                status=status.HTTP_200_OK)
        except Exception as e:
            raise exceptions.APIException(_("Kutilmagan xato ro'y berdi: {}").format(str(e)))

    def delete(self, request, *args, **kwargs):

        author_id = self.kwargs.get('id')

        follower = request.user
        followee = get_object_or_404(User, id=author_id)

        try:
            follow = Follow.objects.get(follower=follower, followee=followee)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            raise exceptions.NotFound(detail=_("Follow relationship not found"))


@extend_schema_view(
    partial_update=extend_schema(
        summary="Update comment",
        request=CommentSerializer,
        responses=default_response(
            (200, CommentSerializer), 400, 401, 404
        )
    ),
    destroy=extend_schema(
        summary="Delete comment",
        request=None,
        responses=default_response(
            (204, None), 400, 401, 404
        )
    )
)
class CommentsView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch', 'delete']


@extend_schema_view(
    post=extend_schema(
        summary="Create a comment",
        request=CommentSerializer,
        responses=default_response(
            (201, CommentSerializer),
            400,
            401,
            404
        )
    )
)
class CreateCommentsView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Article.objects.filter(status=ArticleStatus.PUBLISH)

    def perform_create(self, serializer):
        article_id = self.kwargs.get('id')
        article = generics.get_object_or_404(Article, id=article_id)
        serializer.save(article=article, user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Article detail comments",
        request=None,
        responses=default_response(
            (200, CommentResponseSerializer),
            400,
            401,
            404
        )
    )
)
class ArticleDetailCommentsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleDetailCommentsSerializer

    def get_queryset(self):
        article_id = self.kwargs.get('id')
        return Article.objects.filter(id=article_id)


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
        responses=default_response(
            201, 400, 401, 404
        )
    ),
    delete=extend_schema(
        summary="Delete Favorite",
        request=None,
        responses=default_response(
            (204, None), 400, 401, 404
        )
    ))
class FavoriteArticleView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        favorite, is_created = Favorite.objects.get_or_create(
            user=request.user, article=article)
        if is_created:
            return Response({'detail': _("Maqola sevimlilarga qo'shildi.")}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': _("Maqola sevimlilarga allaqachon qo'shilgan.")}, status=status.HTTP_400_BAD_REQUEST)

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
        responses=default_response(
            (201, ClapSerializer), 400, 401, 404
        )
    ),
    delete=extend_schema(
        summary="Undo Claps",
        request=None,
        responses=default_response(
            (204, None), 400, 401, 404
        )
    )
)
class ClapView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClapSerializer

    def get_queryset(self):
        return Article.objects.filter(status=ArticleStatus.PUBLISH)

    def post(self, request, id):
        user = request.user
        article = get_object_or_404(self.get_queryset(), id=id)

        clap, is_created = Clap.objects.get_or_create(user=user, article=article)
        clap.count = min(clap.count + 1, 50)
        clap.save()

        response_serializer = self.serializer_class(clap)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        article = get_object_or_404(self.get_queryset(), id=id)

        try:
            clap = Clap.objects.get(user=user, article=article)
            clap.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Clap.DoesNotExist:
            raise exceptions.NotFound


@extend_schema_view(
    get=extend_schema(
        summary="Popular Authors recommendations with reads count",
        request=None,
        responses=default_response(
            (200, UserSerializer), 400, 401, 404
        )
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
        responses=default_response(
            (200, ArticleListSerializer), 400, 401, 404
        )
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
        user_id = self.request.user.id
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
        user_id = self.request.user.id
        return User.objects.filter(followers__follower_id=user_id, is_active=True)


@extend_schema_view(
    post=extend_schema(
        summary="Recommend More Articles",
        request=RecommendationSerializer,
        responses=default_response(
            (204, None), 400, 401, 404
        )
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
        serializer.is_valid(raise_exception=True)
        user = request.user
        more_article_id = serializer.validated_data.get('more_article_id')
        less_article_id = serializer.validated_data.get('less_article_id')

        recommendation, is_created = Recommendation.objects.get_or_create(user=user)

        if more_article_id:
            article = get_object_or_404(Article, id=more_article_id, status=ArticleStatus.PUBLISH)
            topics = article.topics.all()

            for topic in topics:
                if recommendation.less.filter(id=topic.id).exists():
                    recommendation.less.remove(topic)
                recommendation.more.add(topic)

        if less_article_id:
            article = get_object_or_404(Article, id=less_article_id, status=ArticleStatus.PUBLISH)
            topics = article.topics.all()

            for topic in topics:
                if recommendation.more.filter(id=topic.id).exists():
                    recommendation.more.remove(topic)
                recommendation.less.add(topic)

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary="Get user notifications",
        request=None,
        responses=default_response(
            (200, NotificationSerializer(many=True)), 400, 401, 404
        )
    ),
    retrieve=extend_schema(
        summary="Retrieve a notification",
        request=None,
        responses=default_response(
            (200, NotificationSerializer), 400, 401, 404
        )
    ),
    partial_update=extend_schema(
        summary="Update user notifications",
        request=None,
        responses=default_response(
            (204, None), 400, 401, 404
        )
    )
)
class UserNotificationView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, read_at__isnull=True)


    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.read_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    post=extend_schema(
        summary="Report article",
        request=None,
        responses=default_response(
            200, 201, 400, 401, 404
        )
    )
)
class ReportArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        article_id = kwargs.get('id')

        article = get_object_or_404(Article, id=article_id, status=ArticleStatus.PUBLISH)

        if article.reports.filter(user=user).exists():
            raise exceptions.ValidationError(_('Ushbu maqola allaqachon shikoyat qilingan.'))

        report = Report.objects.create(article=article)
        report.user.add(user)

        unique_reporters_count = article.reports.values('user').distinct().count()

        if unique_reporters_count > 3:
            article.status = ArticleStatus.TRASH
            article.save(update_fields=['status'])
            return Response({"detail": _("Maqola bir nechta shikoyatlar tufayli olib tashlandi.")}, status=status.HTTP_200_OK)

        return Response({"detail": _("Shikoyat yuborildi.")}, status=status.HTTP_201_CREATED)

@extend_schema_view(
    get=extend_schema(
        summary="FAQs",
        request=None,
        responses=default_response(
            (200, FAQSerializer), 400
        )
    )
)
class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]
