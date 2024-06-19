import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers

serializer_name = 'UserSerializer'
view_name = 'UserViewSet'
view_path = 'users.views'
model_name = 'User'
app_name = 'users'


@pytest.mark.order(3)
@pytest.mark.django_db
def test_users_viewset_class_exists():
    try:
        from users.views import UserViewSet
    except ImportError:
        assert False, f"{view_name} class missing from {view_path}"
    User = get_user_model()

    assert hasattr(UserViewSet, 'queryset'), f"{view_name} queryset missing"
    assert getattr(UserViewSet, 'queryset') is not None, f"{view_name} queryset missing"
    assert hasattr(UserViewSet.queryset, 'model'), f"{view_name} queryset model missing"
    assert UserViewSet.queryset.model is User, f"{view_name} queryset model incorrect. " \
                                               f"Expected {model_name}, got {UserViewSet.queryset.model}"

    assert hasattr(UserViewSet, 'serializer_class'), f"{view_name} serializer_class missing"
    assert getattr(UserViewSet, 'serializer_class') is not None, f"{view_name} serializer_class missing"
    serializer = UserViewSet.serializer_class
    assert serializer.__name__ == serializer_name
    assert issubclass(serializer, serializers.ModelSerializer), f"{serializer_name} is not a ModelSerializer"
    assert hasattr(serializer, 'Meta'), f"{serializer_name} Meta missing"
    assert getattr(serializer, 'Meta') is not None, f"{serializer_name} Meta missing"
    assert hasattr(serializer.Meta, 'model'), f"{serializer_name} Meta model missing"
    assert serializer.Meta.model is User, f"{serializer_name} Meta model incorrect. " \
                                          f"Expected {model_name}, got {serializer.Meta.model}"
    assert hasattr(serializer.Meta, 'fields'), f"{serializer_name} Meta fields missing"
    assert getattr(serializer.Meta, 'fields') is not None, f"{serializer_name} Meta fields missing"
    assert serializer.Meta.fields == ["id", "username", "email", "first_name", "last_name",
                                      "is_staff", "is_active", "last_login", "date_joined"]
