import pytest
from apistar import test

from apistar_contrib.sessions import local
from tests.test_local_session.app import app


@pytest.fixture
def client():
    client = test.TestClient(app)
    yield client
    local.local_memory_sessions = {}


def test_init_session(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {}


def test_write_session(client):
    response = client.get('/?foo=bar')
    assert response.status_code == 200
    assert response.json() == {'foo': 'bar'}


def test_clear_session(client):
    response = client.get('/?foo=bar')
    assert response.status_code == 200
    assert response.json() == {'foo': 'bar'}
    response = client.get('/clear')
    assert response.status_code == 200
    assert response.json() == {}
