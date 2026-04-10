"""上游密钥解析与基址解析的单元测试。

覆盖 tasks 4.1 ~ 4.4：
  - 请求头 Authorization → 上游密钥
  - 模型映射 api_key 回退
  - 无密钥时为空
  - 全局 proxy_api_key / PROXY_API_KEY 不参与解析
  - get_url() 仅读持久化，不读 env
  - 基址缺失时返回空字符串
"""

import copy
import json
import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.pop('PROXY_TARGET_URL', None)
os.environ.pop('PROXY_API_KEY', None)
os.environ['ACCESS_API_KEY'] = 'test-access-key-for-unit-tests'

import settings
from routes.common import extract_upstream_api_key


class FakeRequest:
    def __init__(self, headers=None):
        self.headers = headers or {}


# ─── extract_upstream_api_key ──────────────────────


def test_bearer_token():
    req = FakeRequest({'Authorization': 'Bearer sk-test-123'})
    assert extract_upstream_api_key(req) == 'sk-test-123'


def test_x_api_key():
    req = FakeRequest({'x-api-key': 'xk-abc'})
    assert extract_upstream_api_key(req) == 'xk-abc'


def test_bearer_takes_precedence():
    req = FakeRequest({'Authorization': 'Bearer sk-main', 'x-api-key': 'xk-alt'})
    assert extract_upstream_api_key(req) == 'sk-main'


def test_no_auth_header():
    req = FakeRequest({})
    assert extract_upstream_api_key(req) == ''


def test_empty_bearer():
    req = FakeRequest({'Authorization': 'Bearer '})
    assert extract_upstream_api_key(req) == ''


def test_non_bearer_auth():
    req = FakeRequest({'Authorization': 'Basic abc123'})
    assert extract_upstream_api_key(req) == ''


# ─── settings.get_url() ───────────────────────────


def test_get_url_from_persisted(tmp_path, monkeypatch):
    sf = tmp_path / 'settings.json'
    sf.write_text(json.dumps({'proxy_target_url': 'https://my-relay.com'}))
    monkeypatch.setattr(settings, 'SETTINGS_FILE', str(sf))
    monkeypatch.setattr(settings, '_cache', None)
    settings.load()
    assert settings.get_url() == 'https://my-relay.com'


def test_get_url_empty_no_env_fallback(tmp_path, monkeypatch):
    sf = tmp_path / 'settings.json'
    sf.write_text(json.dumps({'proxy_target_url': ''}))
    monkeypatch.setattr(settings, 'SETTINGS_FILE', str(sf))
    monkeypatch.setattr(settings, '_cache', None)
    monkeypatch.setenv('PROXY_TARGET_URL', 'https://should-not-use.com')
    settings.load()
    assert settings.get_url() == ''


def test_get_url_missing_file_no_env(tmp_path, monkeypatch):
    sf = tmp_path / 'nonexistent.json'
    monkeypatch.setattr(settings, 'SETTINGS_FILE', str(sf))
    monkeypatch.setattr(settings, '_cache', None)
    monkeypatch.setenv('PROXY_TARGET_URL', 'https://should-not-use.com')
    settings.load()
    assert settings.get_url() == ''


# ─── resolve_model 密钥不含全局回退 ──────────────


def test_resolve_model_no_global_key(tmp_path, monkeypatch):
    sf = tmp_path / 'settings.json'
    sf.write_text(json.dumps({
        'proxy_target_url': 'https://relay.com',
        'proxy_api_key': 'should-be-ignored',
        'model_mappings': {},
    }))
    monkeypatch.setattr(settings, 'SETTINGS_FILE', str(sf))
    monkeypatch.setattr(settings, '_cache', None)
    settings.load()
    result = settings.resolve_model('gpt-4')
    assert result['api_key'] == ''


def test_resolve_model_mapping_key(tmp_path, monkeypatch):
    sf = tmp_path / 'settings.json'
    sf.write_text(json.dumps({
        'proxy_target_url': 'https://relay.com',
        'model_mappings': {
            'my-model': {
                'upstream_model': 'real-model',
                'backend': 'openai',
                'api_key': 'mapping-key-123',
            },
        },
    }))
    monkeypatch.setattr(settings, 'SETTINGS_FILE', str(sf))
    monkeypatch.setattr(settings, '_cache', None)
    settings.load()
    result = settings.resolve_model('my-model')
    assert result['api_key'] == 'mapping-key-123'


def test_resolve_model_no_env_key_fallback(tmp_path, monkeypatch):
    sf = tmp_path / 'settings.json'
    sf.write_text(json.dumps({
        'proxy_target_url': 'https://relay.com',
        'model_mappings': {},
    }))
    monkeypatch.setattr(settings, 'SETTINGS_FILE', str(sf))
    monkeypatch.setattr(settings, '_cache', None)
    monkeypatch.setenv('PROXY_API_KEY', 'env-key-should-not-use')
    settings.load()
    result = settings.resolve_model('gpt-4')
    assert result['api_key'] == ''
