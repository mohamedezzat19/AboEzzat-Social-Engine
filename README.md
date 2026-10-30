# AboEzzat Social Engine

A standalone media extraction service for AboEzzat Share New and AboEzzat Receiver.

## Current capabilities

- `GET /health` — service health.
- `POST /api/v1/extract` — extract a supported media URL.
- Direct URL recognition for MP4, HLS, DASH and common audio extensions.
- Optional yt-dlp adapter for supported public pages on YouTube, Facebook, Instagram, TikTok, X/Twitter and Threads.
- Normalized response with title, thumbnail, format URLs, quality, stream type and non-secret request headers.
- Bearer-token authentication for extraction requests.
- Basic URL validation and an allowlist for platform adapters.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set API_BEARER_TOKEN to a long random secret in .env
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Extraction:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"url":"https://example.com/video.mp4"}'
```

## Configuration

- `API_BEARER_TOKEN`: private token shared only with AboEzzat clients.
- `ENABLE_YTDLP`: set to `false` to disable the platform adapter.
- `REQUEST_TIMEOUT_SECONDS`: extraction timeout.
- `ENVIRONMENT`: set to `production` for production safeguards.

An AboEzzat client may send its current WebView cookie header in the optional `cookies` request field over HTTPS. It is used only for that extraction attempt, is excluded from response serialization, and is never forwarded to the TV. Do not commit real tokens, cookies, passwords or session files. Do not log authorization headers or cookies.

## Important limitations

Platform extraction is best-effort and depends on each site's current markup, availability, region and session requirements. DRM-protected, private, login-restricted or otherwise inaccessible content is not bypassed. The adapter does not download media files; it returns candidate playback formats. Some streams may expire or require additional request headers.

The current platform adapter has not yet been verified against live links from every platform. A green CI run verifies the service tests, not successful playback on a Fire TV or Android TV. Receiver integration and real-device playback tests are still pending.

## Development

```bash
pytest -q
```

GitHub Actions runs the test suite on pushes to `main` and pull requests.
