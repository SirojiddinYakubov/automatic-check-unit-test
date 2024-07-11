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
         views.ArticleReadView.as_view(), name='article-reads')
]
