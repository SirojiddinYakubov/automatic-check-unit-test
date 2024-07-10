from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articles', views.ArticlesView, basename='articles')
router.register(r'topics', views.TopicsView, basename='topics')

urlpatterns = [
    path('', include(router.urls)),
    path('topics/follow/', views.TopicFollowView.as_view(), name='topic-follow'),
]
