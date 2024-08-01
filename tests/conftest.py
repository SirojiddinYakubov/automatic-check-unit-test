import pytest
import fakeredis
from pytest_factoryboy import register
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from tests.factories.article_factory import (
    ArticleFactory, TopicFactory, CommentFactory,
    FavoriteFactory, ClapFactory, ReadingHistoryFactory,
    FollowFactory, PinFactory, NotificationFactory, FAQFactory)
from tests.factories.user_factory import UserFactory

register(UserFactory)
register(ArticleFactory)
register(TopicFactory)
register(CommentFactory)
register(FavoriteFactory)
register(ClapFactory)
register(ReadingHistoryFactory)
register(FollowFactory)
register(PinFactory)
register(NotificationFactory)
register(FAQFactory)


@pytest.fixture
def api_client():
    def _api_client(token=None):
        client = APIClient(raise_request_exception=False)
        if token:
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client

    return _api_client


@pytest.fixture
def tokens():
    def _tokens(user):
        refresh = RefreshToken.for_user(user)
        access = str(getattr(refresh, 'access_token'))
        return access, refresh

    return _tokens


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis()



# def pytest_itemcollected(item):
#     # Custom test names
#     custom_names = {
#         'test_users_app_exists': 'Check if users app exists',
#         'test_users_viewset': 'Verify users viewset functionality',
#         'test_create_user': 'Ensure user creation works'
#     }
#
#     # Change the name of the test if it exists in the custom names dictionary
#     if item.originalname in custom_names:
#         item._nodeid = custom_names[item.originalname]
