import asyncio
from urllib.parse import urlsplit

from app.config import settings
from app.extractors.base import BaseExtractor
from app.schemas import ExtractResponse, MediaFormat


class YtDlpExtractor(BaseExtractor):
    name = "yt_dlp"

    async def extract(self, url: str) -> ExtractResponse:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._extract_sync, url),
                timeout=settings.request_timeout_seconds,
            )
        except asyncio.TimeoutError:
            return ExtractResponse(
                success=False, extractor=self.name, error_code="EXTRACTION_TIMEOUT",
                message="The platform extractor timed out.",
            )
        except Exception as exc:
            # Do not expose extractor exception text; it can contain private URLs or headers.
            return ExtractResponse(
                success=False, extractor=self.name, error_code="PLATFORM_EXTRACTION_FAILED",
                message=f"yt-dlp could not extract this page ({type(exc).__name__}).",
            )

    def _extract_sync(self, url: str) -> ExtractResponse:
        import yt_dlp

        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "socket_timeout": settings.request_timeout_seconds,
            "ignoreerrors": False,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return ExtractResponse(
                success=False, extractor=self.name, error_code="NO_MEDIA",
                message="The page did not return playable media.",
            )

        raw_formats = info.get("formats") or []
        if info.get("url"):
            raw_formats = raw_formats + [info]

        formats = []
        seen = set()
        for item in raw_formats:
            media_url = item.get("url")
            if not media_url or item.get("has_drm"):
                continue
            protocol = (item.get("protocol") or "").lower()
            extension = (item.get("ext") or "").lower()
            if "m3u8" in protocol:
                kind = "hls"
            elif "dash" in protocol or extension == "mpd":
                kind = "dash"
            elif extension in {"mp4", "m4v"}:
                kind = "mp4"
            elif extension in {"m4a", "mp3", "aac", "opus"}:
                kind = "audio"
            else:
                kind = "unknown"

            # Do not forward credentials/cookies from extractor metadata to the TV.
            headers = {
                str(k): str(v) for k, v in (item.get("http_headers") or {}).items()
                if str(k).lower() not in {"cookie", "authorization", "proxy-authorization"}
            }
            key = (media_url, kind)
            if key in seen:
                continue
            seen.add(key)
            height = item.get("height")
            quality = f"{height}p" if height else (item.get("format_note") or item.get("format_id"))
            formats.append(MediaFormat(
                url=media_url,
                quality=str(quality) if quality else None,
                type=kind,
                headers=headers,
            ))

        if not formats:
            return ExtractResponse(
                success=False, platform=urlsplit(url).hostname,
                extractor=self.name, error_code="NO_PLAYABLE_FORMATS",
                message="The page was found, but no non-DRM playable formats were returned.",
                requires_cookies=bool(info.get("login_required")),
            )

        formats.sort(key=lambda f: (f.type != "mp4", f.quality or ""), reverse=False)
        return ExtractResponse(
            success=True,
            platform=info.get("extractor_key") or urlsplit(url).hostname,
            title=info.get("title"),
            thumbnail=info.get("thumbnail"),
            formats=formats[:12],
            requires_cookies=bool(info.get("login_required")),
            extractor=self.name,
        )
