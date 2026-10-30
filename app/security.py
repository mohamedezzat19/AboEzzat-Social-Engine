import ipaddress
import socket
from urllib.parse import urlsplit

from fastapi import Header, HTTPException

from app.config import settings


def validate_public_http_url(value: str) -> str:
    if len(value) > settings.max_url_length:
        raise HTTPException(status_code=413, detail="URL is too long")

    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Only absolute HTTP(S) URLs are supported")
    if parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="Credentials in URLs are not allowed")

    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost"} or host.endswith(".localhost") or host.endswith(".local"):
        raise HTTPException(status_code=400, detail="Local network URLs are not allowed")

    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)}
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="URL host could not be resolved")

    if not addresses:
        raise HTTPException(status_code=400, detail="URL host could not be resolved")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise HTTPException(status_code=400, detail="Private or reserved network destinations are not allowed")
    return value.strip()


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    expected = settings.api_bearer_token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    supplied = authorization[7:].strip()
    if not expected or supplied != expected:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
