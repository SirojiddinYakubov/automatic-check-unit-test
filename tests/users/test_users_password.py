import pytest
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from tests.factories.user_factory import UserFactory
from users.services import UserService

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize("old_password, new_password", [
    ('test_password', 'new_password123'),
    ('another_test_password', 'another_new_password456'),
])
def test_change_password(api_client, old_password, new_password):

    user = UserFactory.create()
    user.set_password(old_password)
    user.save()

    tokens = UserService.create_tokens(user)
    access_token = tokens['access']

    change_password_url = reverse('change-password')
    new_password_data = {
        'old_password': old_password,
        'new_password': new_password
    }
    response = api_client(token=access_token).post(change_password_url, data=new_password_data)

    assert response.status_code == status.HTTP_200_OK, f"Failed to change password. Response: {response.content}"
    assert User.objects.get(username=user.username).check_password(new_password), "Parol o'zgartirilmadi"
