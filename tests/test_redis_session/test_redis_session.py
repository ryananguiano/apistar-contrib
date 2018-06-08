import pytest
from apistar import test

from apistar_contrib.compat import redis
from tests.test_redis_session.app import app, REDIS_URL


@pytest.fixture(scope='module')
def redis_client():
    client = redis.StrictRedis.from_url(REDIS_URL)
    client.ping()
    yield client
    client.flushdb()


@pytest.fixture
def client(redis_client):
    client = test.TestClient(app)
    yield client


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
