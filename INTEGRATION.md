# AboEzzat client integration contract

This is the shared contract for Share New and Receiver. The service must be deployed behind HTTPS before either Android app is pointed at it.

## Share New request

Send a POST request to `/api/v1/extract`:

```http
POST /api/v1/extract
Authorization: Bearer <private-service-token>
Content-Type: application/json
```

```json
{
  "url": "https://www.instagram.com/reel/EXAMPLE/",
  "cookies": "sessionid=...; csrftoken=..."
}
```

The `cookies` property is optional. Only send cookies belonging to the exact site being extracted, over HTTPS. Never put cookies or the bearer token in logs, analytics, crash reports, or user-visible notifications.

## Successful response

```json
{
  "success": true,
  "platform": "Instagram",
  "title": "Example video",
  "thumbnail": "https://cdn.example/image.jpg",
  "formats": [
    {
      "url": "https://cdn.example/video.mp4",
      "quality": "720p",
      "type": "mp4",
      "headers": {
        "Referer": "https://www.instagram.com/"
      },
      "expires_at": null
    }
  ],
  "requires_cookies": false,
  "extractor": "yt_dlp",
  "error_code": null,
  "message": null
}
```

Example values above are illustrative, not live extraction results.

## Receiver handoff

Share New should choose a playable format, then send Receiver:
- the direct media URL,
- the format type,
- the non-secret request headers returned for that format,
- the title and thumbnail when available.

Do not forward the original page cookies or service bearer token to Receiver. The service bearer token belongs only between Share New and the extraction API. If a media CDN requires cookies, the current response intentionally does not forward them; this case needs an explicit, narrowly scoped design before enabling it.

## Failure handling

- HTTP 401: missing or invalid service token.
- HTTP 413: URL too long.
- HTTP 422: invalid request body.
- HTTP 400: invalid or blocked URL.
- `success=false`: extraction did not produce a playable format; show a concise notification and offer browser fallback.
- `EXTRACTION_TIMEOUT`: allow one controlled retry, then stop.
- `NO_PLAYABLE_FORMATS`: do not send the page URL to ExoPlayer.

## Android implementation notes

- Run extraction off the main/UI thread.
- Use bounded connect/read/write timeouts and cancel the request when the user cancels.
- Do not log request bodies or Authorization headers.
- Keep the API base URL and bearer token out of source control. Use a secure build secret / runtime configuration.
- Receiver must use the returned headers when creating the ExoPlayer MediaItem / DataSource.
- For YouTube, Share New may route to the user's selected YouTube-compatible TV app instead of sending a page URL to ExoPlayer.
