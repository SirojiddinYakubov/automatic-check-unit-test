import pytest
from django.conf import settings

app_name = 'users'


@pytest.mark.order(1)
@pytest.mark.django_db
def test_users_app_exists():
    try:
        import users  # noqa
    except ImportError:
        assert False, f"{app_name} app folder missing"
    assert app_name in settings.INSTALLED_APPS, f"{app_name} app not installed"
