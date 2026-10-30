from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.config import settings
from app.main import app
from app.schemas import ExtractRequest
import app.security as security


def test_extract_requires_bearer_token():
    client = TestClient(app)
    response = client.post("/api/v1/extract", json={"url": "https://example.com/video.mp4"})
    assert response.status_code == 401


def test_direct_media_extraction(monkeypatch):
    settings.api_bearer_token = "test-secret"
    monkeypatch.setattr(
        security.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("93.184.216.34", 0))],
    )
    client = TestClient(app)
    response = client.post(
        "/api/v1/extract",
        headers={"Authorization": "Bearer test-secret"},
        json={"url": "https://example.com/clip.mp4"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["formats"][0]["type"] == "mp4"


def test_cookie_header_is_not_serialized():
    payload = ExtractRequest(url="https://www.instagram.com/reel/example/", cookies="sessionid=private")
    assert "cookies" not in payload.model_dump()


def test_cookie_header_rejects_newlines():
    with pytest.raises(ValidationError):
        ExtractRequest(url="https://www.instagram.com/reel/example/", cookies="sessionid=a\r\nInjected: yes")
