import pytest
from apistar import test, exceptions

from apistar_contrib.csrf.settings import CsrfSettings
from tests.test_csrf.app import app


@pytest.fixture
def client():
    return test.TestClient(app)


@pytest.fixture
def settings():
    return CsrfSettings({})


def test_show_form(client):
    response = client.get('/')
    assert response.status_code == 200


def test_post_no_csrf(client):
    with pytest.raises(exceptions.Forbidden):
        client.post('/handle')


def test_post_csrf_token(client, settings):
    response = client.get('/')
    csrf_token = response.cookies.get(settings.CSRF_COOKIE_NAME)
    response = client.post('/handle', {settings.CSRF_TOKEN_FIELD_NAME: csrf_token})
    assert response.status_code == 200
