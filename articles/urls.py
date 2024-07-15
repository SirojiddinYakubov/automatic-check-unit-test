from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articles', views.ArticlesView, basename='articles')
router.register(r'comments', views.CommentView, basename='comments')
router.register(r'notification', views.UserNotificationView, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<int:article_id>/clap/',
         views.ClapView.as_view(), name='article-clap'),
    path('articles/<int:article_id>/increment/reads-count/',
         views.ArticleReadView.as_view(), name='article-reads'),
    path('authors/pinned/', views.UserPinnedArticles.as_view(),
         name='user-articles-pinned'),
    path('authors/follow/', views.AuthorFollowView.as_view(), name='author-follow'),
    path('authors/popular/', views.PopularAuthorsView.as_view(),
         name='popular-authors'),
    path('topics/follow/', views.TopicFollowView.as_view(), name='topic-follow'),
    path('search/', views.SearchView.as_view(), name='article-search'),
    path('favorite/<int:pk>/', views.FavoriteArticleView.as_view(),
         name='favorite-article'),
    path('users/favorites/', views.UserFavoritesListView.as_view(),
         name='user-favorites'),
    path('users/reading-hestory/',
         views.ReadingHistoryView.as_view(), name='reading-hestory'),
    path('users/<int:user_id>/followers/',
         views.FollowersListView.as_view(), name='followers'),
    path('users/<int:user_id>/following/',
         views.FollowingListView.as_view(), name='following'),
    path('users/recommend/', views.RecommendationView.as_view(), name='recommend'),
    path('topics/report/', views.ReportTopicView.as_view(), name='report-topic'),
    path('faqs/', views.FAQListView.as_view(), name='faq-list'),
]
