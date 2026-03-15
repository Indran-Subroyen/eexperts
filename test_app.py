import json
from unittest.mock import patch, Mock

import pytest

from app import app, _cache


@pytest.fixture
def client():
    app.config["TESTING"] = True
    _cache.clear()  # start each test with a clean cache
    with app.test_client() as client:
        yield client


# fake gist data so we don't need to hit GitHub for every unit test
MOCK_GISTS = [
    {
        "id": "abc123",
        "description": "Test gist",
        "html_url": "https://gist.github.com/abc123",
        "files": {"hello.py": {"filename": "hello.py"}},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
]


# --- Unit tests (mocked, no real API calls) ---

@patch("app.requests.get")
def test_user_gists_returns_list(mock_get, client):
    # hit /<username> and check we get the gist back with the right id, description, files
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GISTS
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    resp = client.get("/testuser")
    data = json.loads(resp.data)

    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == "abc123"
    assert data[0]["description"] == "Test gist"
    assert data[0]["files"] == ["hello.py"]


@patch("app.requests.get")
def test_user_not_found(mock_get, client):
    # simulate GitHub returning 404 — our API should also return 404 with an error message
    mock_resp = Mock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    resp = client.get("/nonexistent-user-xyz")
    data = json.loads(resp.data)

    assert resp.status_code == 404
    assert "error" in data


@patch("app.requests.get")
def test_response_shape(mock_get, client):
    # make sure each gist object only has the 6 fields we want, nothing extra from GitHub
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GISTS
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    resp = client.get("/testuser")
    data = json.loads(resp.data)

    expected_keys = {"id", "description", "url", "files", "created_at", "updated_at"}
    assert set(data[0].keys()) == expected_keys


def test_healthz(client):
    # just checking /healthz returns 200 and {"status": "ok"}
    resp = client.get("/healthz")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["status"] == "ok"


@patch("app.requests.get")
def test_pagination_params(mock_get, client):
    # when we pass ?page=2&per_page=5, those should get forwarded to the GitHub API call
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GISTS
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    client.get("/testuser?page=2&per_page=5")

    _, kwargs = mock_get.call_args
    assert kwargs["params"] == {"page": 2, "per_page": 5}


@patch("app.requests.get")
def test_caching(mock_get, client):
    # request the same user twice — GitHub should only be called once, second one comes from cache
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GISTS
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    client.get("/testuser")
    client.get("/testuser")

    assert mock_get.call_count == 1


# --- Integration test (hits the real GitHub API) ---

def test_octocat_live(client):
    # this one actually calls GitHub — octocat test account
    resp = client.get("/octocat")
    data = json.loads(resp.data)

    assert resp.status_code == 200
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "url" in data[0]
