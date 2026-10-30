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

## Deployment policy (current phase)

This project is **free and personal-use only** in its current phase:

- No paid VPS, cloud hosting, domain, subscription, or external API account is required.
- The only intended clients are the user's own AboEzzat Share New and AboEzzat Receiver apps.
- Keep the service private. Do not publish its port to the public internet or expose an unauthenticated endpoint.
- The default Docker Compose port binding is loopback-only (`127.0.0.1`). This is suitable for local development on the same computer.
- A phone or TV cannot use another computer's `127.0.0.1`. For a personal home-LAN test, the owner may deliberately bind the service to a private LAN interface and allow only trusted devices through the router/firewall. Use a strong private bearer token and do not configure router port-forwarding.
- No hosting provider or Linux VPS has been selected or needs to be purchased. Any remote deployment or additional users are explicitly deferred until the owner chooses to expand.

The intended future integration is limited to Share New submitting extraction requests and Receiver playing the returned media URL. The Receiver should not become a public extraction server.

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

## Personal home-network use (no paid hosting)

If you have a computer that can stay on at home, the service can be used by Share over the same trusted Wi-Fi network. This is still a local personal service, not cloud hosting.

1. Copy `.env.example` to `.env`.
2. Generate a private token with `openssl rand -hex 32` and put it in `API_BEARER_TOKEN`.
3. Keep `SOCIAL_ENGINE_BIND_IP=127.0.0.1` for same-computer testing. For a phone/TV on the same trusted home Wi-Fi, change it to `0.0.0.0` and allow inbound TCP 8000 only on the private/home network in the computer firewall.
4. Start with `docker compose up -d --build`.
5. Find the computer's private LAN IPv4 address (for example `192.168.1.20`) and configure Share's Social Engine address as `http://192.168.1.20:8000`, with the same bearer token.
6. Do not enable router port-forwarding, do not use public Wi-Fi, and return `SOCIAL_ENGINE_BIND_IP` to `127.0.0.1` when LAN access is no longer needed.

The LAN bind is an explicit opt-in. The default remains loopback-only. A computer running the service must be powered on and reachable for Share to use it. No computer/server available? Keep the Social Engine connection disabled for now; the local Share extractors remain separate.

## Important limitations

Platform extraction is best-effort and depends on each site's current markup, availability, region and session requirements. DRM-protected, private, login-restricted or otherwise inaccessible content is not bypassed. The adapter does not download media files; it returns candidate playback formats. Some streams may expire or require additional request headers.

The current platform adapter has not yet been verified against live links from every platform. A green CI run verifies the service tests, not successful playback on a Fire TV or Android TV. Receiver integration and real-device playback tests are still pending.

## Development

```bash
pytest -q
```

GitHub Actions runs the test suite on pushes to `main` and pull requests.
