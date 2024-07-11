import os
from secrets import token_urlsafe
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from users.enums import TokenType
from users.exceptions import OTPException
from django.contrib.auth.hashers import make_password
from django.utils import translation
from django.conf import settings
from modeltranslation.translator import translator

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
    url = '/users/signup/'
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
        url = '/users/me/'
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
    url = '/users/login/'
    resp = api_client().post(url, data=req_json)
    assert resp.status_code == status_code
    if status_code == status.HTTP_200_OK:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['access', 'refresh'])

        # check access token
        client = api_client(token=resp_json['access'])
        url = '/users/me/'
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
    url = '/users/me/'
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
                'first_name': 'abdulaziz',
                'last_name': 'komilov',
                'middle_name': 'sobirovich',
                'email': 'test@uz.uz',
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
    url = '/users/me/'

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


@pytest.fixture
def change_password_data(request, user_factory, tokens):
    old_password = 'strong_password_123'
    new_password = 'new_password_123'
    user = user_factory.create(password=old_password)
    access, _ = tokens(user)

    def valid_password():
        return (
            200, user, access,
            {
                'old_password': old_password,
                'new_password': new_password
            }
        )

    def incorrect_password():
        return (
            400, user, access,
            {
                'old_password': '<PASSWORD>',
                'new_password': new_password
            }
        )

    def invalid_old_password():
        return (
            400, user, access,
            {
                'old_password': 'asdf*&^%',
                'new_password': new_password
            },
        )

    def empty_old_password():
        return (
            400, user, access,
            {
                'old_password': '',
                'new_password': new_password
            },
        )

    def required_old_password():
        return (
            400, user, access,
            {
                'new_password': new_password
            },
        )

    def invalid_new_password():
        return (
            400, user, access,
            {
                'old_password': old_password,
                'new_password': old_password
            },
        )

    def empty_new_password():
        return (
            400, user, access,
            {
                'old_password': old_password,
                'new_password': ''
            },
        )

    def required_new_password():
        return (
            400, user, access,
            {
                'old_password': old_password,
            },
        )

    def inactive_user():
        user.is_active = False
        user.save()
        return 401, user, 'fake-token', {}

    def unauthorized_user():
        return 401, user, 'fake-token', {}

    data = {
        'valid_password': valid_password,
        'incorrect_password': incorrect_password,
        'invalid_old_password': invalid_old_password,
        'empty_old_password': empty_old_password,
        'required_old_password': required_old_password,
        'invalid_new_password': invalid_new_password,
        'empty_new_password': empty_new_password,
        'required_new_password': required_new_password,
        'inactive_user': inactive_user,
        'unauthorized_user': unauthorized_user
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'change_password_data',
    [
        'valid_password',
        # 'incorrect_password',
        # 'invalid_old_password',
        # 'empty_old_password',
        # 'required_old_password',
        # 'invalid_new_password',
        # 'empty_new_password',
        # 'required_new_password',
        # 'inactive_user',
        # 'unauthorized_user'
    ],
    indirect=True,
)
def test_change_password(change_password_data, api_client):
    status_code, user, access, data = change_password_data()
    client = api_client(token=access)
    resp = client.put('/users/password/change/', data, format='json')
    print("blabla", resp.data)
    assert resp.status_code == status_code

    if resp.status_code == status.HTTP_200_OK:
        user.refresh_from_db()
        assert user.check_password(data['new_password'])

        client = api_client()
        login_url = '/users/login/'
        login_data = {
            'username': user.username,
            'password': data['new_password']
        }

        login_resp = client.post(login_url, login_data, format='json')

        resp_json = login_resp.json()
        assert sorted(resp_json.keys()) == sorted(['access', 'refresh'])


@pytest.fixture
def logout_data(request, user_factory, api_client, tokens, mocker):
    def valid_without_stored_tokens():
        user = user_factory.create()
        access, _ = tokens(user)
        return 200, api_client(access), user, access

    def valid_with_stored_tokens():
        user = user_factory.create()
        access, _ = tokens(user)
        return 200, api_client(access), user, access

    def invalid_with_unauthorized_user():
        return 401, api_client(), mocker.Mock(id="f0f9f100-3abd-4bbf-88ad-0cfdd6953aca"), None

    data = {
        'valid_without_stored_tokens': valid_without_stored_tokens,
        'valid_with_stored_tokens': valid_with_stored_tokens,
        'invalid_with_unauthorized_user': invalid_with_unauthorized_user,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'logout_data',
    [
        'valid_without_stored_tokens',
        'valid_with_stored_tokens',
        'invalid_with_unauthorized_user',
    ],
    indirect=True,
)
def test_logout(logout_data, mocker, fake_redis, request, tokens):
    status_code, client, user, access = logout_data()
    test_name = request.node.name

    mocker.patch('users.services.TokenService.get_redis_client', return_value=fake_redis)

    # add tokens to fake_redis
    if test_name == 'test_logout[valid_with_stored_tokens]':
        _, refresh = tokens(user)
        access_token_key = f"user:{user.id}:{TokenType.ACCESS}"
        refresh_token_key = f"user:{user.id}:{TokenType.REFRESH}"
        fake_redis.sadd(access_token_key, access)
        fake_redis.sadd(refresh_token_key, str(refresh))

    # users-me get data
    if test_name == 'test_logout[valid_with_stored_tokens]':
        url = '/users/me/'
        resp = client.get(url)
        assert resp.status_code == status_code

    # logout
    resp = client.post('/users/logout/')
    assert resp.status_code == status_code

    # users-me get data after logout
    if status_code == 200:
        resp = client.get('/users/me/')
        assert resp.status_code == 401

    if test_name == 'test_logout[valid_with_stored_tokens]':
        access_token_key = f"user:{user.id}:{TokenType.ACCESS}"
        refresh_token_key = f"user:{user.id}:{TokenType.REFRESH}"
        assert fake_redis.smembers(access_token_key) == {b'fake_token'}
        assert fake_redis.smembers(refresh_token_key) == {b'fake_token'}


@pytest.fixture
def forgot_password_data(request, user_factory):
    user = user_factory.create()
    user.save()

    def valid_data():
        return (
            200, user,
            {
                'email': user.email,
            }
        )

    def not_exist_email():
        return (
            404, user,
            {
                'email': 'test@gmail.com',
            }
        )

    def invalid_email():
        return (
            400, user,
            {
                'email': 'testgmail.com',
            }
        )

    def empty_email():
        return (
            400, user,
            {
                'email': '',
            }
        )

    def required_email():
        return (
            400, user,
            {}
        )

    data = {
        'valid_data': valid_data,
        'not_exist_email': not_exist_email,
        'invalid_email': invalid_email,
        'empty_email': empty_email,
        'required_email': required_email,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'forgot_password_data',
    [
        'valid_data',
        'not_exist_email',
        'invalid_email',
        'empty_email',
        'required_email'
    ],
    indirect=True,
)
def test_forgot_password_view(forgot_password_data, api_client, mocker):
    status_code, user, data = forgot_password_data()
    generate_otp_mock = mock.Mock(return_value=("567483", "sdNdFhKSt_0p2cbzygxcI9A75doUwSYocr1vTqkjxeM"))
    mocker.patch('users.services.OTPService.generate_otp', generate_otp_mock)
    mock_redis_conn = mocker.Mock()
    mocker.patch('users.services.OTPService.get_redis_conn', return_value=mock_redis_conn)
    client = api_client()
    resp = client.post('/users/password/forgot/', data, format='json')
    assert resp.status_code == status_code
    if status_code == status.HTTP_200_OK:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['email', 'otp_secret'])
        assert resp.data['email'] == user.email

        # check send email error
        key = f"{user.email}:otp"
        mocker.patch(
            'users.services.SendEmailService.send_email',
            mock.Mock(side_effect=Exception('Error sending email.'))
        )
        resp = client.post('/users/password/forgot/', data, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        mock_redis_conn.delete.assert_called_once_with(key)


@pytest.fixture
def forgot_password_verify_data(request, user_factory, mocker):
    user = user_factory.create()

    otp_code = "123456"
    otp_secret = "sdNdFhKSt_0p2cbzygxcI9A75doUwSYocr1vTqkjxeM"

    def valid_data():
        return (
            200, user, otp_secret, None,
            {
                'email': user.email,
                'otp_code': otp_code,
            }
        )

    def not_exist_email():
        return (
            404, user, otp_secret, None,
            {
                'email': 'test@gmail.com',
                'otp_code': otp_code,
            }
        )

    def inactive_user():
        user.is_active = False
        user.save()
        return (
            404, user, otp_secret, None,
            {
                'email': user.email,
                'otp_code': otp_code,
            }
        )

    def invalid_email():
        return (
            400, user, otp_secret, None,
            {
                'email': 'fake_email',
                'otp_code': otp_code,
            }
        )

    def empty_email():
        return (
            400, user, otp_secret, None,
            {
                'email': '',
                'otp_code': otp_code,
            }
        )

    def required_email():
        return (
            400, user, otp_secret, None,
            {
                'otp_code': otp_code,
            }
        )

    def invalid_otp_code():
        return (
            400, user, otp_secret, OTPException('Invalid OTP code.'),
            {
                'email': user.email,
                'otp_code': '000000',
            }
        )

    def empty_otp_code():
        return (
            400, user, otp_secret, None,
            {
                'email': user.email,
                'otp_code': '',
            }
        )

    def required_otp_code():
        return (
            400, user, otp_secret, None,
            {
                'email': user.email,
            }
        )

    def invalid_otp_secret():
        return (
            400, user, 'fake-otp-secret', OTPException('Invalid OTP code.'),
            {
                'email': user.email,
                'otp_code': otp_code,
            }
        )

    def empty_otp_secret():
        return (
            404, user, '', None,
            {
                'email': user.email,
                'otp_code': otp_code,
            }
        )

    def required_otp_secret():
        return (
            404, user, '', None,
            {
                'email': user.email,
                'otp_code': otp_code,
            }
        )

    data = {
        'valid_data': valid_data,
        'not_exist_email': not_exist_email,
        'inactive_user': inactive_user,
        'invalid_email': invalid_email,
        'empty_email': empty_email,
        'required_email': required_email,
        'invalid_otp_code': invalid_otp_code,
        'empty_otp_code': empty_otp_code,
        'required_otp_code': required_otp_code,
        'invalid_otp_secret': invalid_otp_secret,
        'empty_otp_secret': empty_otp_secret,
        'required_otp_secret': required_otp_secret,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'forgot_password_verify_data',
    [
        'valid_data',
        'not_exist_email',
        'inactive_user',
        'invalid_email',
        'empty_email',
        'required_email',
        'invalid_otp_code',
        'empty_otp_code',
        'required_otp_code',
        'invalid_otp_secret',
        'empty_otp_secret',
        'required_otp_secret',
    ],
    indirect=True,
)
def test_forgot_password_verify_view(forgot_password_verify_data, api_client, mocker):
    status_code, user, otp_secret, check_otp_side_effect, data = forgot_password_verify_data()
    redis_conn = mocker.Mock()
    mocker.patch('users.services.OTPService.get_redis_conn', return_value=redis_conn)
    mocker.patch('users.services.OTPService.check_otp', side_effect=check_otp_side_effect)
    mock_token_hash = make_password(token_urlsafe())
    mocker.patch('users.views.make_password', return_value=mock_token_hash)
    client = api_client()
    resp = client.post(f'/users/password/forgot/verify/{otp_secret}/', data, format='json')
    assert resp.status_code == status_code
    if resp.status_code == status.HTTP_200_OK:
        resp_json = resp.json()
        key = f"{user.email}:otp"
        redis_conn.delete.assert_called_once_with(key)
        redis_conn.set.assert_called_once_with(mock_token_hash, user.email, ex=2 * 60 * 60)
        assert 'token' in resp_json
        assert resp_json['token'] == mock_token_hash


@pytest.fixture
def reset_password_view_data(request, user_factory):
    user = user_factory.create()
    token_hash = make_password(token_urlsafe())
    new_password = "new_password123"

    def valid_data():
        return (
            200, user.email, {
                "token": token_hash,
                "password": new_password
            }
        )

    def inactive_user():
        user.is_active = False
        user.save()
        return (
            404, user.email, {
                "token": token_hash,
                "password": new_password
            }
        )

    def not_exist_email():
        return (
            404, 'not_exist_email', {
                "token": token_hash,
                "password": new_password
            }
        )

    def empty_token():
        return (
            400, user.email, {
                "token": '',
                "password": new_password
            }
        )

    def required_token():
        return (
            400, user.email, {
                "password": new_password
            }
        )

    def invalid_password():
        return (
            400, user.email, {
                "token": token_hash,
                "password": '123'
            }
        )

    def empty_password():
        return (
            400, user.email, {
                "token": token_hash,
                "password": ''
            }
        )

    def required_password():
        return (
            400, user.email, {
                "token": token_hash
            }
        )

    data = {
        'valid_data': valid_data,
        'inactive_user': inactive_user,
        'not_exist_email': not_exist_email,
        'empty_token': empty_token,
        'required_token': required_token,
        'invalid_password': invalid_password,
        'empty_password': empty_password,
        'required_password': required_password
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reset_password_view_data',
    [
        'valid_data',
        'inactive_user',
        'not_exist_email',
        'empty_token',
        'required_token',
        'invalid_password',
        'empty_password',
        'required_password',

    ],
    indirect=True,
)
def test_reset_password_view(reset_password_view_data, api_client, mocker):
    status_code, email, data = reset_password_view_data()
    mock_redis_conn = mocker.Mock()
    mocker.patch('users.services.OTPService.get_redis_conn', return_value=mock_redis_conn)
    mocker.patch('users.services.UserService.create_tokens',
                 return_value={'access': 'access_token', 'refresh': 'refresh_token'})
    mock_redis_conn.get.return_value = email.encode() if email else None

    client = api_client()
    resp = client.patch('/users/password/reset/', data, format='json')

    if resp.status_code != 400:
        mock_redis_conn.get.assert_called_once_with(data['token'])

    assert resp.status_code == status_code
    if resp.status_code == status.HTTP_200_OK:
        mock_redis_conn.delete.assert_called_once_with(data['token'])
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['access', 'refresh'])

        user = User.objects.get(email=email)
        assert user.check_password(data['password']) is True


@pytest.mark.django_db
def test_modeltranslation_is_setup_correctly(user_factory):
    assert translator.get_options_for_model(User) is not None

    instance = user_factory.create(first_name="Test")

    for lang_code, _ in settings.LANGUAGES:
        field_name = f'first_name_{lang_code}'
        assert hasattr(instance, field_name), f"{field_name} not found in {User.__name__}"

    instance.first_name_en = "English name"
    instance.first_name_uz = "O'zbekcha ism"
    instance.first_name_ru = "Русское имя"
    instance.save()

    instance.refresh_from_db()

    with translation.override('en'):
        assert instance.first_name == "English name"
    with translation.override('uz'):
        assert instance.first_name == "O'zbekcha ism"
    with translation.override('ru'):
        assert instance.first_name == "Русское имя"
