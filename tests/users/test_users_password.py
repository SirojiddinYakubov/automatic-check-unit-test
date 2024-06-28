import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.services import UserService

User = get_user_model()


@pytest.fixture
def user_password(request):
    def valid_password():
        return (
            200,
            {
                'old_password': 'password123',
                'new_password': 'new_password'
            }
        )

    def valid_password2():
        return (
            200,
            {
                'old_password': 'old_password',
                'new_password': 'new_password'
            }
        )

    def empty_data():
        return (
            400,
            {
                'old_password': '',
                'new_password': ''
            }
        )

    data = {
        'valid_password': valid_password,
        'valid_password2': valid_password2,
        'empty_data': empty_data
    }
    return data[request.param]



@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_password',
    [
        'valid_password',
        'valid_password2',
        'empty_data'
    ],
    indirect=True,
)
def test_change_password(api_client, user_factory, user_password):
    status_code, data = user_password()

    user = user_factory.create()
    user.set_password(data['old_password'])
    user.save()

    tokens = UserService.create_tokens(user)
    access_token = tokens['access']

    change_password_url = reverse('change-password')
    new_password_data = {
        'old_password': data['old_password'],
        'new_password': data['new_password']
    }
    response = api_client(token=access_token).post(change_password_url, data=new_password_data)

    assert response.status_code == status_code, f"Failed to change password. Response: {response.content}"
    assert User.objects.get(username=user.username).check_password(data['new_password']), "Parol o'zgartirilmadi"
