import pytest
from django.conf import settings

app_name = 'rest_framework'


@pytest.mark.order(1)
@pytest.mark.django_db
def test_rest_framework_installed():
    try:
        import rest_framework
    except ImportError:
        assert False, f"{app_name} app missing"
    assert app_name in settings.INSTALLED_APPS, f"{app_name} app not installed"
