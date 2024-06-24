import pytest
from django.conf import settings

app_name = 'shares'


@pytest.mark.order(2)
@pytest.mark.django_db
# @pytest.mark.parametrize("test_input", [""], ids=["Check if users app exists"])
def test_shares_app_exists():
    try:
        import shares
    except ImportError:
        assert False, f"{app_name} app folder missing"
    assert app_name in settings.INSTALLED_APPS, f"{app_name} app not installed"

    try:
        import shares.views
    except ImportError:
        assert False, f"{app_name}.views file missing"

    try:
        import shares.serializers
    except ImportError:
        assert False, f"{app_name}.serializers file missing"

    try:
        import shares.urls
    except ImportError:
        assert False, f"{app_name}.urls file missing"
