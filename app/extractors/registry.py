from app.config import settings
from app.extractors.http_direct import HttpDirectExtractor
from app.extractors.ytdlp_adapter import YtDlpExtractor
from app.security import is_allowed_platform_host
from app.schemas import ExtractResponse


class ExtractorRegistry:
    def __init__(self) -> None:
        self._direct = HttpDirectExtractor()
        self._platform = YtDlpExtractor() if settings.enable_ytdlp else None

    async def extract(self, url: str, cookies: str | None = None) -> ExtractResponse:
        direct = await self._direct.extract(url)
        if direct.success:
            return direct

        from urllib.parse import urlsplit
        host = (urlsplit(url).hostname or "").lower()
        if self._platform and is_allowed_platform_host(host):
            return await self._platform.extract(url, cookies=cookies)

        return ExtractResponse(
            success=False,
            extractor="registry",
            error_code="UNSUPPORTED_URL",
            message="No enabled extractor supports this URL. No login or DRM restrictions are bypassed.",
        )


registry = ExtractorRegistry()
