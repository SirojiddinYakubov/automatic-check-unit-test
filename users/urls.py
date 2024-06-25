from django.urls import path
from .views import SignupView, LoginView, Me

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', Me.as_view(), name='me'),
]
