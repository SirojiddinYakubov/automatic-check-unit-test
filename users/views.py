from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()



@extend_schema_view(
    post=extend_schema(
        summary="Sign up a new user",
        responses={
            201: UserSerializer,
            400: 'Validation Error'
        }
    )
)
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema_view(
    post=extend_schema(
        summary="Log in a user",
        responses={
            200: 'Login successful',
            400: 'Validation Error'
        }
    )
)
class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Get user information",
        responses={
            200: UserSerializer,
        }
    )
)
class UsersMe(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "middle_name": user.middle_name,
            "avatar": user.avatar.url if user.avatar else None,
            "date_joined": user.date_joined,
        }
        return Response(user_data, status=status.HTTP_200_OK)
