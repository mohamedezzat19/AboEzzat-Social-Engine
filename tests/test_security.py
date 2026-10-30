import pytest
from fastapi import HTTPException

from app.security import is_allowed_platform_host, validate_public_http_url


def test_rejects_non_http_scheme():
    with pytest.raises(HTTPException):
        validate_public_http_url("file:///etc/passwd")


def test_rejects_localhost():
    with pytest.raises(HTTPException):
        validate_public_http_url("http://localhost/private")


def test_platform_allowlist_matches_subdomains_only():
    assert is_allowed_platform_host("www.instagram.com")
    assert is_allowed_platform_host("m.facebook.com")
    assert not is_allowed_platform_host("instagram.com.attacker.example")
    assert not is_allowed_platform_host("example.com")
