from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
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
