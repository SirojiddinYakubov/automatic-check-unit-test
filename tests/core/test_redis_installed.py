import pytest
from django.conf import settings


@pytest.mark.order(1)
@pytest.mark.django_db
def test_redis_installed():
    try:
        import django_redis  # noqa
    except ImportError:
        assert False, "django_redis package is not installed"
    assert 'django_redis' in settings.INSTALLED_APPS, "django_redis package is not installed"
    assert 'default' in settings.CACHES
    assert settings.CACHES['default']['BACKEND'] == 'django_redis.cache.RedisCache'
