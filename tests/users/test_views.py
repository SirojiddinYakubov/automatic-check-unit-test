import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def signup_data(request):
    password = 'FGHF2342^%$'

    def valid_data():
        return (
            201,
            {
                'username': 'test',
                'email': 'test@test.com',
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov',
                'middle_name': 'Tojiddinovich',
                'password': password
            },
        )

    def invalid_username():
        return (
            400,
            {
                'username': {'foo': 'bar'},
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov',
                'password': password
            },
        )

    def empty_username():
        return (
            400,
            {
                'username': '',
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov',
                'password': password
            },
        )

    def required_username():
        return (
            400,
            {
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov',
                'password': password
            },
        )

    def invalid_first_name():
        return (
            400,
            {
                'username': 'test',
                'first_name': {'foo': 'bar'},
                'last_name': 'Yakubov',
                'password': password
            },
        )

    def empty_first_name():
        return (
            400,
            {
                'username': 'test',
                'first_name': '',
                'last_name': 'Yakubov',
                'password': password
            },
        )

    def required_first_name():
        return (
            400,
            {
                'username': 'test',
                'last_name': 'Yakubov',
                'password': password
            },
        )

    def invalid_last_name():
        return (
            400,
            {
                'username': 'test',
                'first_name': 'Sirojiddin',
                'last_name': {'foo': 'bar'},
                'password': password
            },
        )

    def empty_last_name():
        return (
            400,
            {
                'username': 'test',
                'first_name': 'Sirojiddin',
                'last_name': '',
                'password': password
            },
        )

    def required_last_name():
        return (
            400,
            {
                'username': 'test',
                'first_name': 'Sirojiddin',
                'password': password
            },
        )

    def invalid_password():
        return (
            400,
            {
                'username': 'test',
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov',
                'password': {'foo': 'bar'}
            },
        )

    def empty_password():
        return (
            400,
            {
                'username': 'test',
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov',
                'password': ''
            },
        )

    def required_password():
        return (
            400,
            {
                'username': 'test',
                'first_name': 'Sirojiddin',
                'last_name': 'Yakubov'
            },
        )

    data = {
        'valid_data': valid_data,
        'invalid_username': invalid_username,
        'empty_username': empty_username,
        'required_username': required_username,
        'invalid_first_name': invalid_first_name,
        'empty_first_name': empty_first_name,
        'required_first_name': required_first_name,
        'invalid_last_name': invalid_last_name,
        'empty_last_name': empty_last_name,
        'required_last_name': required_last_name,
        'invalid_password': invalid_password,
        'empty_password': empty_password,
        'required_password': required_password,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'signup_data',
    [
        'valid_data',
        'invalid_username',
        'empty_username',
        'required_username',
        'invalid_first_name',
        'empty_first_name',
        'required_first_name',
        'invalid_last_name',
        'empty_last_name',
        'required_last_name',
        'invalid_password',
        'empty_password',
        'required_password',
    ],
    indirect=True,
)
def test_signup(signup_data, api_client):
    client = api_client()
    status_code, req_json = signup_data()
    url = reverse('signup')
    resp = client.post(url, data=req_json, format='json')
    assert resp.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(
            ['user', 'access', 'refresh']
        )
        assert sorted(resp_json['user'].keys()) == sorted(
            ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email']
        )

        # check database and response
        user = User.objects.get(username=resp_json['user']['username'])
        assert user.first_name == resp_json['user']['first_name'] == 'Sirojiddin'
        assert user.last_name == resp_json['user']['last_name'] == 'Yakubov'
        assert user.middle_name == resp_json['user']['middle_name'] == 'Tojiddinovich'
        assert user.email == resp_json['user']['email'] == 'test@test.com'
        assert user.username == resp_json['user']['username'] == 'test'

        # check access token
        client = api_client(token=resp_json['access'])
        url = reverse('users-me')
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK


@pytest.fixture
def login_data(request, user_factory):
    username = 'test'
    password = 'random_password'
    user = user_factory.create(username=username, password=password)

    def valid_username():
        return (
            200, {
                'username': user.username,
                'password': password,
            },
        )

    def required_username():
        return (
            400, {
                'password': password,
            },
        )

    def empty_username():
        return (
            400, {
                'username': '',
                'password': password,
            },
        )

    def required_password():
        return (
            400, {
                'username': user.email,
            },
        )

    def empty_password():
        return (
            400, {
                'username': user.email,
                'password': '',
            },
        )

    def invalid_password():
        return (
            400, {
                'username': user.email,
                'password': 'fake_password',
            },
        )

    data = {
        'valid_username': valid_username,
        'required_username': required_username,
        'empty_username': empty_username,
        'required_password': required_password,
        'empty_password': empty_password,
        'invalid_password': invalid_password,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'login_data',
    [
        'valid_username',
        'required_username',
        'empty_username',
        'required_password',
        'empty_password',
        'invalid_password',
    ],
    indirect=True,
)
def test_login(login_data, api_client):
    status_code, req_json = login_data()
    url = reverse('login')
    resp = api_client().post(url, data=req_json)
    assert resp.status_code == status_code
    if status_code == status.HTTP_200_OK:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['access', 'refresh'])

        # check access token
        client = api_client(token=resp_json['access'])
        url = reverse('users-me')
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK


@pytest.fixture
def user_me_data(request, user_factory, tokens):
    def valid_user():
        user = user_factory.create()
        access, _ = tokens(user)
        return 200, access

    def inactive_user():
        user = user_factory.create(is_active=False)
        access, _ = tokens(user)
        return 401, access

    def unauthorized_user():
        return 401, "fake_token"

    data = {
        'valid_user': valid_user,
        'inactive_user': inactive_user,
        'unauthorized_user': unauthorized_user,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_me_data',
    [
        'valid_user',
        'inactive_user',
        'unauthorized_user',
    ],
    indirect=True,
)
def test_user_me(user_me_data, api_client):
    status_code, access = user_me_data()

    client = api_client(token=access)
    url = reverse('users-me')
    resp = client.get(url)
    assert resp.status_code == status_code
    if status_code == status.HTTP_200_OK:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(
            ['id', 'first_name', 'last_name', 'middle_name', 'email', 'username']
        )
        user = User.objects.get(id=resp_json['id'])
        assert resp_json['first_name'] == user.first_name
        assert resp_json['last_name'] == user.last_name
        assert resp_json['middle_name'] == user.middle_name
        assert resp_json['username'] == user.username
        assert resp_json['email'] == user.email


@pytest.fixture
def user_update_data(request, user_factory, tokens):
    user = user_factory.create()
    access, _ = tokens(user)

    def valid_update():
        return (
            200,
            access,
            {
                'first_name': 'Abdulaziz',
                'last_name': 'Komilov',
                'middle_name': 'Sobirovich',
                'email': 'abdulaziz@email.com',
            }
        )

    def invalid_update():
        return (
            400,
            access,
            {
                'first_name': 'Abdulaziz',
                'last_name': 'Komilov',
                'email': 'userEmail'
            }
        )

    def empty_data():
        return (
            200,
            access,
            {
                'first_name': '',
                'last_name': '',
                'middle_name': '',
                'email': ''
            }
        )

    def unauthorized_user():
        return (
            401,
            "token",
            {
                'first_name': 'Name',
                'last_name': 'LastName',
                'middle_name': 'MiddleName',
                'email': 'email@test.com'
            }
        )

    def valid_update_with_avatar():
        return (
            200,
            access,
            {
                'first_name': 'ABDULAZIZ',
                'last_name': 'KOMILOV',
                'middle_name': 'TEST',
                'email': 'TESTS@TESTS.COM',
                'avatar': (
                    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
                    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
                    b'\x02\x4c\x01\x00\x3b'
                )
            }
        )

    data = {
        'valid_update': valid_update,
        'invalid_update': invalid_update,
        'empty_data': empty_data,
        'unauthorized_user': unauthorized_user,
        'valid_update_with_avatar': valid_update_with_avatar,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_update_data',
    [
        'valid_update',
        'invalid_update',
        'empty_data',
        'unauthorized_user',
        'valid_update_with_avatar',
    ],
    indirect=True,
)
def test_user_me_patch(user_update_data, api_client):
    status_code, access, update_data = user_update_data()

    client = api_client(token=access)
    url = reverse('users-me')

    if 'avatar' in update_data:
        avatar_data = update_data['avatar']
        avatar_file = SimpleUploadedFile(f"{update_data['first_name']}.gif", avatar_data, content_type="image/gif")
        update_data['avatar'] = avatar_file
        resp = client.patch(url, data=update_data, format='multipart')
    else:
        resp = client.patch(url, data=update_data)

    assert resp.status_code == status_code

    if status_code == status.HTTP_200_OK:
        resp_json = resp.json()
        assert resp_json['first_name'] == update_data.get('first_name', '')
        assert resp_json['last_name'] == update_data.get('last_name', '')
        assert resp_json['middle_name'] == update_data.get('middle_name', '')
        assert resp_json['email'] == update_data.get('email', '')

        user = User.objects.get(id=resp_json['id'])
        assert user.first_name == update_data.get('first_name')
        assert user.last_name == update_data.get('last_name')
        assert user.middle_name == update_data.get('middle_name', '')
        assert user.email == update_data.get('email')

        if 'avatar' in update_data:
            user.refresh_from_db()
            assert user.avatar is not None, "Avatar was not uploaded correctly"
            avatar_path = user.avatar.name
            assert avatar_path.startswith(f'users/avatars/{user.username}')
            assert avatar_path.endswith('.gif'), f"Expected avatar path to end with '.gif', got '{avatar_path}'"
            expected_avatar_filename = f"{user.username}.gif"
            assert os.path.basename(
                avatar_path) == expected_avatar_filename, f"Avatar filename mismatch: expected '{expected_avatar_filename}', got '{os.path.basename(avatar_path)}'"
