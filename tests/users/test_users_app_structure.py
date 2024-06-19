import pytest
from django.conf import settings

app_name = 'users'


@pytest.mark.order(1)
@pytest.mark.django_db
# @pytest.mark.parametrize("test_input", [""], ids=["Check if users app exists"])
def test_users_app_exists():
    try:
        import users
    except ImportError:
        assert False, f"{app_name} app folder missing"
    assert app_name in settings.INSTALLED_APPS, f"{app_name} app not installed"

    try:
        import users.views
    except ImportError:
        assert False, f"{app_name}.views file missing"

    try:
        import users.serializers
    except ImportError:
        assert False, f"{app_name}.serializers file missing"

    try:
        import users.urls
    except ImportError:
        assert False, f"{app_name}.urls file missing"
