from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from articles.views import ( UserNotificationView, AuthorFollowView,
    PopularAuthorsView, FollowersListView,
    FollowingListView, RecommendationView)

router = DefaultRouter()
router.register(r'notifications', UserNotificationView, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('me/', views.UsersMe.as_view(), name='users-me'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change-password'),
    path('password/forgot/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('password/forgot/verify/<str:otp_secret>/', views.ForgotPasswordVerifyView.as_view(), name="forgot-verify"),
    path('password/reset/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('<int:id>/follow/', AuthorFollowView.as_view(), name='author-follow'),
    path('articles/popular/', PopularAuthorsView.as_view(),
         name='popular-authors'),
    path('followers/',
         FollowersListView.as_view(), name='followers'),
    path('following/',
         FollowingListView.as_view(), name='following'),
    path('recommend/', RecommendationView.as_view(), name='recommend'),
]
