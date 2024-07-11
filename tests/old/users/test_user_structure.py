import os

import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import SimpleUploadedFile

model_name = 'CustomUser'
app_name = 'users'


@pytest.mark.order(2)
@pytest.mark.django_db
def test_custom_user_model():
    assert settings.AUTH_USER_MODEL == f"{app_name}.{model_name}", f"{model_name} model not set"
    CustomUser = get_user_model()  # noqa
    assert CustomUser is not None, f"{model_name} model not found"
    assert issubclass(CustomUser, AbstractUser), f"{model_name} model not a subclass of AbstractUser"

    assert CustomUser._meta.db_table == "user", f"{model_name} model db_table not set"
    assert CustomUser._meta.verbose_name == "User", f"{model_name} model verbose_name not set"
    assert CustomUser._meta.verbose_name_plural == "Users", f"{model_name} model verbose_name_plural not set"
    assert CustomUser._meta.ordering == ["-date_joined"], f"{model_name} model ordering not set"

    user = CustomUser.objects.create(
        username='test',
        first_name='Sirojiddin',
        last_name='Yoqubov',
        middle_name='Tojiddinovich',
        email='test@test.com'
    )

    assert user is not None, f"{model_name} model not created"
    user.set_password('test')
    user.save()
    assert user.check_password('test'), f"{model_name} model password not set"
    assert user.full_name == 'Yoqubov Sirojiddin Tojiddinovich', f"{model_name} model full_name not set"
    assert user.email == 'test@test.com', f"{model_name} model email not set"
    assert user.username == 'test', f"{model_name} model username not set"

    old_avatar = os.path.join(settings.MEDIA_ROOT, f"users/avatars/{user.username}.gif")
    if os.path.exists(old_avatar):
        os.remove(old_avatar)

    # Test the avatar upload functionality
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    avatar = SimpleUploadedFile(f"{user.username}.gif", small_gif, content_type="image/gif")
    user.avatar = avatar
    user.save()

    expected_avatar_path = os.path.join('users/avatars', f'{user.username}.gif')
    assert user.avatar.name == expected_avatar_path, f"Avatar not uploaded correctly: {user.avatar.name}"

    full_avatar_path = os.path.join(settings.MEDIA_ROOT, expected_avatar_path)
    assert os.path.exists(full_avatar_path), f"Avatar file not found at {full_avatar_path}"


@pytest.mark.order(3)
def test_custom_user_admin():
    CustomUser = get_user_model()  # noqa
    try:
        import users.admin  # noqa
    except ImportError:
        assert False, f"{app_name}.admin missing"

    try:
        CustomUserAdmin = admin.site._registry[CustomUser]  # noqa
    except KeyError:
        assert False, f"{model_name} model not registered in admin"

    assert CustomUserAdmin is not None, f"{model_name} model not registered in admin"

    fieldset_fields = frozenset(field for fieldset in CustomUserAdmin.fieldsets for field in fieldset[1]['fields'])
    expected_fields = frozenset(['middle_name', 'avatar'])
    assert fieldset_fields.intersection(
        expected_fields) == expected_fields, f"{model_name} model fields {expected_fields} not in fieldset"

    assert CustomUserAdmin.list_display == (
        'id', 'username', 'email', 'first_name', 'last_name', 'middle_name'), f"{model_name} model list_display not set"
    assert CustomUserAdmin.list_display_links == (
        'id', 'username', 'email'), f"{model_name} model list_display_links not set"
    assert CustomUserAdmin.search_fields == (
        'username', 'email', 'first_name', 'last_name', 'middle_name'), f"{model_name} model search_fields not set"
    assert CustomUserAdmin.list_filter == (
        'last_login', 'date_joined', 'is_staff', 'is_superuser', 'is_active'), f"{model_name} model list_filter not set"
