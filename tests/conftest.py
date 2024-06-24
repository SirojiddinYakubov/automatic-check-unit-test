import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    def _api_client(token=None):
        client = APIClient(raise_request_exception=False)
        if token:
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client

    return _api_client


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
