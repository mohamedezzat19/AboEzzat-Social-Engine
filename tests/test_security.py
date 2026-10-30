import pytest
from fastapi import HTTPException

from app.security import validate_public_http_url


def test_rejects_non_http_scheme():
    with pytest.raises(HTTPException):
        validate_public_http_url("file:///etc/passwd")


def test_rejects_localhost():
    with pytest.raises(HTTPException):
        validate_public_http_url("http://localhost/private")
