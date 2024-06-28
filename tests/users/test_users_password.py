import pytest
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser


@pytest.mark.django_db
def test_change_password(api_client):

    user = CustomUser.objects.create(
        username='fake_user',
        first_name='first_name',
        last_name='last_name',
        middle_name='middle_name',
        email='test@test.com'
    )

    password = 'test_password'
    user.set_password(password)
    user.save()

    response = api_client().post(reverse('login'), data={
        'username': user.username,
        'password': password,
    })
    assert response.status_code == status.HTTP_200_OK
    access_token = response.data['access']

    change_password_url = reverse('change-password')
    new_password_data = {
        'old_password': password,
        'new_password': 'new_password123'
    }
    response = api_client(token=access_token).post(change_password_url, data=new_password_data)

    assert response.status_code == status.HTTP_200_OK, f"Failed to change password. Response: {response.content}"
    assert CustomUser.objects.get(username=user.username).check_password(
        'new_password123'), "Password not updated"
