# Deployment

The repository includes a Docker Compose configuration intended to run the API behind a TLS reverse proxy.

## 1. Prepare the host

Install Docker Engine and the Docker Compose plugin on a Linux host. Keep the operating system and Docker updated.

## 2. Configure secrets

Copy .env.example to .env and set:

- ENVIRONMENT=production
- API_BEARER_TOKEN to a long, randomly generated secret (at least 32 random bytes).

Never commit .env or share the bearer token in chat, issue reports, or application logs.

## 3. Build and start

    docker compose build
    docker compose up -d
    docker compose ps
    docker compose logs --tail=100 social-engine

The service binds to 127.0.0.1:8000 only. It is not directly exposed to the public internet.

## 4. HTTPS reverse proxy

Configure a reverse proxy (for example, Caddy or Nginx) to terminate HTTPS and proxy requests to 127.0.0.1:8000. Require HTTPS for every request containing the bearer token or session cookies. Do not enable public plain-HTTP access.

## 5. Verify

    curl http://127.0.0.1:8000/health

Then test /api/v1/extract using the bearer token from the server's secret environment. Do not paste the real token into a public terminal recording or screenshot.

## Security notes

- The compose file uses a read-only container filesystem, drops Linux capabilities, and enables no-new-privileges.
- Add host/network egress controls that block loopback, private, link-local, and cloud metadata IP ranges. Application-level URL checks alone are not a complete SSRF defense, especially when third-party extractors follow redirects or request media hosts.
- Restrict who can reach the reverse proxy and rotate the bearer token if it is exposed.
- Use only content you are authorized to access. DRM, private content and platform access restrictions are not bypassed.
