from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articles', views.ArticlesView, basename='articles')
router.register(r'topics', views.TopicsView, basename='topics')
router.register(r'comments', views.CommentCreateView, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    path('topics/follow/', views.TopicFollowView.as_view(), name='topic-follow'),
    path('search/', views.SearchView.as_view(), name='article-search'),
    path('favorite/<int:pk>/', views.FavoriteArticleView.as_view(),
         name='favorite-article'),
    path('users/favorites/', views.UserFavoritesListView.as_view(),
         name='user-favorites'),
    path('articles/<int:article_id>/clap/',
         views.ClapView.as_view(), name='article-clap'),
    path('articles/<int:article_id>/reads/',
         views.ArticleReadView.as_view(), name='article-reads'),
    path('popular-authors/', views.PopularAuthorsView.as_view(),
         name='popular-authors'),
    path('users/reading-hestory/',
         views.ReadingHistoryView.as_view(), name='reading-hestory'),
    path('author/follow/', views.FollowView.as_view(), name='follow'),
    path('author/unfollow/<int:followee_id>/',
         views.UnfollowView.as_view(), name='unfollow'),
    path('users/<int:user_id>/followers/',
         views.FollowersListView.as_view(), name='followers'),
    path('users/<int:user_id>/following/',
         views.FollowingListView.as_view(), name='following'),
]
