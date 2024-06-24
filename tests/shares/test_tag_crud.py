import pytest
from shares.models import Tag


@pytest.mark.order(13)
@pytest.mark.django_db
def test_create_new_tag(api_client):
    post_json = {
        'name': 'Python',
        'description': 'High level language',
    }
    client = api_client()
    resp = client.post('/tags/', data=post_json, format='json')
    assert resp.status_code == 201, f"POST /tags/ not returned 201. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"POST /tags/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'name', 'description']) == sorted(resp.data.keys())
    assert resp.data['name'] == post_json['name']
    assert resp.data['description'] == post_json['description']
    assert Tag.objects.filter(id=resp.data['id']).exists(), f"Tag {resp.data['id']} not created"


@pytest.mark.order(14)
@pytest.mark.django_db
def test_get_tags_list(api_client):
    test_create_new_tag(api_client)
    client = api_client()
    resp = client.get('/tags/')
    assert resp.status_code == 200, f"GET /tags/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, list), f"GET /tags/ not returned list. Got {type(resp.data)}"
    assert len(resp.data) == 1, f"GET /tags/ returned {len(resp.data)} tags. Expected 1"
    assert sorted(['id', 'name', 'description']) == sorted(resp.data[0].keys())
    assert resp.data[0]['name'] == 'Python'
    assert resp.data[0]['description'] == 'High level language'


@pytest.mark.order(15)
@pytest.mark.django_db
def test_get_tag_by_id(api_client):
    post_json = {
        'name': 'Python',
        'description': 'High level language',
    }
    client = api_client()
    resp = client.post('/tags/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.get(f'/tags/{obj_id}/')
    assert resp.status_code == 200, f"GET /tags/{obj_id}/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"GET /tags/{obj_id}/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'name', 'description']) == sorted(resp.data.keys())
    assert resp.data['id'] == obj_id
    assert resp.data['name'] == post_json['name']
    assert resp.data['description'] == post_json['description']


@pytest.mark.order(16)
@pytest.mark.django_db
def test_get_tag_by_id_not_found(api_client):
    client = api_client()
    resp = client.get(f'/tags/{1000}/')
    assert resp.status_code == 404, f"GET /tags/{1000}/ not returned 404. Got {resp.status_code}"


@pytest.mark.order(17)
@pytest.mark.django_db
def test_tag_update(api_client):
    post_json = {
        'name': 'Python',
        'description': 'High level language',
    }
    put_json = {
        'name': 'Java',
        'description': 'Good language',
    }
    client = api_client()
    resp = client.post('/tags/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.put(f'/tags/{obj_id}/', data=put_json, format='json')
    assert resp.status_code == 200, f"PUT /tags/{obj_id}/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"PUT /tags/{obj_id}/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'name', 'description']) == sorted(resp.data.keys())
    assert resp.data['id'] == obj_id
    assert resp.data['name'] == put_json['name']
    assert resp.data['description'] == put_json['description']


@pytest.mark.order(18)
@pytest.mark.django_db
def test_tag_update_not_found(api_client):
    put_json = {
        'name': 'Java',
        'description': 'Good language',
    }
    client = api_client()
    resp = client.put(f'/tags/{1000}/', data=put_json, format='json')
    assert resp.status_code == 404, f"PUT /tags/{1000}/ not returned 404. Got {resp.status_code}"


@pytest.mark.order(19)
@pytest.mark.django_db
def test_tag_partial_update(api_client):
    post_json = {
        'name': 'Python',
        'description': 'High level language',
    }
    patch_json = {
        'name': 'Java',
    }
    client = api_client()
    resp = client.post('/tags/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.patch(f'/tags/{obj_id}/', data=patch_json, format='json')
    assert resp.status_code == 200, f"PATCH /tags/{obj_id}/ not returned 200. Got {resp.status_code}"
    assert isinstance(resp.data, dict), f"PATCH /tags/{obj_id}/ not returned dict. Got {type(resp.data)}"
    assert sorted(['id', 'name', 'description']) == sorted(resp.data.keys())
    assert resp.data['id'] == obj_id
    assert resp.data['name'] == patch_json['name']
    assert resp.data['description'] == post_json['description']


@pytest.mark.order(20)
@pytest.mark.django_db
def test_tag_delete(api_client):
    post_json = {
        'name': 'Python',
        'description': 'High level language',
    }
    client = api_client()
    resp = client.post('/tags/', data=post_json, format='json')
    obj_id = resp.data['id']
    resp = client.delete(f'/tags/{obj_id}/')
    assert resp.status_code == 204, f"DELETE /tags/{obj_id}/ not returned 204. Got {resp.status_code}"
    assert not Tag.objects.filter(id=obj_id).exists(), f"Tag {obj_id} not deleted"
