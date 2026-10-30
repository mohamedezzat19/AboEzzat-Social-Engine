# AboEzzat Social Engine

A standalone media extraction service for AboEzzat Share New and AboEzzat Receiver.

## Project goals

- Accept a supported public media page URL and return normalized media metadata and playable formats when extraction is permitted.
- Keep platform adapters isolated so individual engines can be enabled or disabled.
- Return required playback headers and format details to the client.
- Never attempt to bypass DRM, authentication, or platform access restrictions.
- Keep secrets, session cookies, and authorization tokens out of logs and source control.

## API contract (initial target)

- `GET /health` — service health.
- `POST /api/v1/extract` — extract media from a page URL.

The API will use a private bearer token for AboEzzat clients. Configure secrets through environment variables; do not commit real credentials.

## Development

The initial implementation will use Python and FastAPI. Automated tests and CI will be added alongside the API skeleton.

## Status

Repository initialized. Extraction support for individual platforms is not yet verified.
