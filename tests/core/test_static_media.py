import pytest
from django.conf import settings


@pytest.mark.order(1)
@pytest.mark.django_db
def test_static_media_settings():
    assert settings.STATIC_URL == '/static/', "STATIC_URL is not set correctly"
    assert settings.STATIC_ROOT == settings.BASE_DIR / "staticfiles", "STATIC_ROOT is not set correctly"
    assert settings.MEDIA_URL == '/media/', "MEDIA_URL is not set correctly"
    assert settings.MEDIA_ROOT == settings.BASE_DIR / "media", "MEDIA_ROOT is not set correctly"
