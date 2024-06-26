import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        if 'password' not in kwargs:
            kwargs['password'] = 'password123'
        return User.objects.create_user(**kwargs)
    return make_user



@pytest.mark.django_db
def test_signup_view(api_client):
    client = api_client()
    url = reverse('signup')
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert 'refresh' in response.data
    assert 'access' in response.data



@pytest.mark.django_db
def test_login_view(api_client, create_user):
    create_user(username='testuser', password='password123')
    client = api_client()
    url = reverse('login')
    data = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'refresh' in response.data
    assert 'access' in response.data



@pytest.mark.django_db
def test_users_me_view(api_client, create_user):
    create_user(username='testuser', password='password123')
    client = api_client()
    url = reverse('login')
    data = {
        'username': 'testuser',
        'password': 'password123'
    }
    login_response = client.post(url, data)
    token = login_response.data['access']

    client = api_client(token=token)
    url = reverse('users-me')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'testuser'
