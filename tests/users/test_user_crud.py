import pytest
from django.contrib.auth import get_user_model


@pytest.mark.order(5)
@pytest.mark.django_db
def test_create_new_user(api_client):
    req_json = {
        'username': 'test',
        'password': 'test',
        'email': 'test@ya.ru',
        'first_name': 'Sirojiddin',
        'last_name': 'Yoqubov',
    }
    client = api_client()
    resp = client.post('/users/', data=req_json, format='json')
    assert resp.status_code == 201, f"POST /users/ not returned 201. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"POST /users/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login',
                   'date_joined']) == sorted(resp.data.keys())
    assert resp.data['username'] == req_json['username']
    assert resp.data['email'] == req_json['email']
    assert resp.data['first_name'] == req_json['first_name']
    assert resp.data['last_name'] == req_json['last_name']

    User = get_user_model()
    assert User.objects.filter(id=resp.data['id']).exists(), f"User {resp.data['id']} not created"


@pytest.mark.order(6)
@pytest.mark.django_db
def test_get_users_list(api_client):
    test_create_new_user(api_client)
    client = api_client()
    resp = client.get('/users/')
    assert resp.status_code == 200, f"GET /users/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, list), f"GET /users/ not returned list. Got {type(resp.data)}"
    assert len(resp.data) == 1, f"GET /users/ returned {len(resp.data)} users. Expected 1"


@pytest.mark.order(7)
@pytest.mark.django_db
def test_get_user_by_id(api_client):
    req_json = {
        'username': 'test',
        'password': 'test',
        'email': 'test@ya.ru',
        'first_name': 'Sirojiddin',
        'last_name': 'Yoqubov',
    }
    client = api_client()
    resp = client.post('/users/', data=req_json, format='json')
    obj_id = resp.data['id']
    resp = client.get(f'/users/{obj_id}/')
    assert resp.status_code == 200, f"GET /users/{obj_id}/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"GET /users/{obj_id}/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login',
                   'date_joined']) == sorted(resp.data.keys())
    assert resp.data['id'] == obj_id
    assert resp.data['username'] == 'test'
    assert resp.data['email'] == 'test@ya.ru'
    assert resp.data['first_name'] == 'Sirojiddin'
    assert resp.data['last_name'] == 'Yoqubov'


@pytest.mark.order(8)
@pytest.mark.django_db
def test_get_user_by_id_not_found(api_client):
    client = api_client()
    resp = client.get(f'/users/{1000}/')
    assert resp.status_code == 404, f"GET /users/{1000}/ not returned 404. Got {resp.status_code}"


@pytest.mark.order(9)
@pytest.mark.django_db
def test_user_update(api_client):
    post_json = {
        'username': 'test',
        'password': 'test',
        'email': 'test@ya.ru',
        'first_name': 'Sirojiddin',
        'last_name': 'Yoqubov',
    }
    put_json = {
        'username': 'new_username',
        'email': 'new_email@ya.ru',
        'first_name': 'New first name',
        'last_name': 'New last name',
    }
    client = api_client()
    resp = client.post('/users/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.put(f'/users/{obj_id}/', data=put_json, format='json')
    assert resp.status_code == 200, f"PUT /users/{obj_id}/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"PUT /users/{obj_id}/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login',
                   'date_joined']) == sorted(resp.data.keys())
    assert resp.data['id'] == obj_id
    assert resp.data['username'] == put_json['username']
    assert resp.data['email'] == put_json['email']
    assert resp.data['first_name'] == put_json['first_name']
    assert resp.data['last_name'] == put_json['last_name']


@pytest.mark.order(10)
@pytest.mark.django_db
def test_user_update_not_found(api_client):
    req_json = {
        'username': 'new_username',
        'email': 'new_email@ya.ru',
        'first_name': 'New first name',
        'last_name': 'New last name',
    }
    client = api_client()
    resp = client.put(f'/users/{1000}/', data=req_json, format='json')
    assert resp.status_code == 404, f"PUT /users/{1000}/ not returned 404. Got {resp.status_code}"


@pytest.mark.order(11)
@pytest.mark.django_db
def test_user_partial_update(api_client):
    post_json = {
        'username': 'username',
        'password': 'test',
        'email': 'test@ya.ru',
        'first_name': 'Sirojiddin',
        'last_name': 'Yoqubov',
    }
    patch_json = {
        'username': 'new_username',
    }
    client = api_client()
    resp = client.post('/users/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.patch(f'/users/{obj_id}/', data=patch_json, format='json')
    assert resp.status_code == 200, f"PATCH /users/{obj_id}/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"PATCH /users/{obj_id}/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login',
                   'date_joined']) == sorted(resp.data.keys())
    assert resp.data['id'] == obj_id
    assert resp.data['username'] == patch_json['username']
    assert resp.data['email'] == post_json['email']
    assert resp.data['first_name'] == post_json['first_name']
    assert resp.data['last_name'] == post_json['last_name']


@pytest.mark.order(12)
@pytest.mark.django_db
def test_user_delete(api_client):
    post_json = {
        'username': 'test',
        'password': 'test',
        'email': 'test@ya.ru',
        'first_name': 'Sirojiddin',
        'last_name': 'Yoqubov',
    }
    client = api_client()
    resp = client.post('/users/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.delete(f'/users/{obj_id}/')
    assert resp.status_code == 204, f"DELETE /users/{obj_id}/ not returned 204. Got {resp.status_code}"

    resp = client.get(f'/users/{obj_id}/')
    assert resp.status_code == 404, f"GET /users/{obj_id}/ not returned 404. Got {resp.status_code}"

    User = get_user_model()
    assert not User.objects.filter(id=obj_id).exists(), f"User {obj_id} not deleted"
