"""ACCESS_API_KEY：启动必填、仅管理 API 校验、非管理路径不凭此返回 401。"""

import pytest


@pytest.fixture
def access_key():
    return 'mgmt-key-test'


@pytest.fixture
def app(monkeypatch, access_key):
    monkeypatch.setenv('ACCESS_API_KEY', access_key)
    from app import create_app

    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_app_exits_when_access_key_missing(monkeypatch):
    monkeypatch.delenv('ACCESS_API_KEY', raising=False)
    from app import create_app

    with pytest.raises(SystemExit):
        create_app()


def test_health_ok_without_access_headers(client):
    assert client.get('/health').status_code == 200


def test_v1_models_ok_without_access_headers(client):
    assert client.get('/v1/models').status_code == 200


def test_admin_settings_401_without_auth_header(client):
    assert client.get('/api/admin/settings').status_code == 401


def test_admin_settings_401_wrong_bearer(client):
    r = client.get('/api/admin/settings', headers={'Authorization': 'Bearer wrong'})
    assert r.status_code == 401


def test_admin_settings_200_with_correct_bearer(client, access_key):
    r = client.get(
        '/api/admin/settings',
        headers={'Authorization': f'Bearer {access_key}'},
    )
    assert r.status_code == 200
